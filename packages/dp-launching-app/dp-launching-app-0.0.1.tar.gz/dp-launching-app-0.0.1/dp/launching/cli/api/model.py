import os
import json
import sys
import traceback
import logging
from pathlib import Path
from fastapi import FastAPI, status as HTTP_STATUS
from pydantic.error_wrappers import ValidationError
from kubernetes import client, config
from typing import Union, Optional

from dp.launching.typing.basic import BaseModel
from dp.launching.cli.utils.random import get_random_str

from pydantic_cli import to_runner_sp
from pydantic_cli import to_runner as origin_to_runner

IS_DEBUG_MODE = os.getenv("PROD_ENV") == None

if IS_DEBUG_MODE:
    config.load_kube_config()
else:
    config.load_incluster_config()


TMP_PATH_PREFIX = "/tmp/uploaded_files"


def compare_cpu_cores(cpu1: str, cpu2: str):
    cpu1 = cpu1.replace("m", "")
    cpu2 = cpu2.replace("m", "")

    def parse_cpu(cpu):
        try:
            return float(cpu)
        except ValueError:
            return 0.0

    cpu1_val = parse_cpu(cpu1)
    cpu2_val = parse_cpu(cpu2)

    return cpu1_val > cpu2_val


def convert_memory_to_bytes(memory_str):
    units = {
        "Ki": 1024,
        "Mi": 1024**2,
        "Gi": 1024**3,
        "Ti": 1024**4,
        "Pi": 1024**5,
        "Ei": 1024**6,
    }
    number = "".join(filter(str.isdigit, memory_str))
    unit = "".join(filter(str.isalpha, memory_str))

    return int(number) * units.get(unit, 1)


def compare_memory(mem1: str, mem2: str):
    mem1_bytes = convert_memory_to_bytes(mem1)
    mem2_bytes = convert_memory_to_bytes(mem2)

    return mem1_bytes > mem2_bytes


def get_max_core_and_memory_from_cluster():
    try:
        v1 = client.CoreV1Api()
        nodes = v1.list_node().items
        max_cpu = 0
        max_memory = 0

        for node in nodes:
            cpu = node.status.capacity.get("cpu")
            memory = node.status.capacity.get("memory")

            memory_mib = (
                int(memory[:-2]) // (1024**2)
                if memory.endswith("Ki")
                else int(memory[:-2])
            )

            max_cpu = max(max_cpu, int(cpu))
            max_memory = max(max_memory, memory_mib)

        logging.info(f"Max CPU across all nodes: {max_cpu}")
        logging.info(f"Max Memory across all nodes: {max_memory} Gi")
        return max_cpu, max_memory
    except Exception as err:
        logging.error(f"get max cpu and memory failed: {err}")
        return 1, 1


SERVICE_START_CONFIG = "start-service"
SERVICE_API_PREFIX = "/api"
SERVICE_API_VERSION = "v1"
SERVICE_STATUS_ERROR = "error"
SERVICE_STATUS_SUCCESS = "success"

VALIDATE_ONLY_RUNNER = lambda *_, **__: 0


class ErrHandler:
    errors = None

    def __init__(self):
        self.errors = {}

    def __call__(self, ex: ValidationError) -> int:
        return self.error_handler(ex)

    def get_errors(self):
        return self.errors

    def error_handler(self, ex: ValidationError) -> int:
        self.errors["error_type"] = (
            hasattr(ex, "__class__")
            and hasattr(ex.__class__, "__name__")
            and ex.__class__.__name__
        ) or "OtherErr"
        self.errors["message"] = str(ex)
        exc_type, exc_value, exc_tb = sys.exc_info()
        err_stack = traceback.format_exception(exc_type, exc_value, exc_tb)
        self.errors["error_stacks"] = err_stack
        return 1


def get_opentool_service_ns():
    return "opentool-service"


def get_opentool_jobs_ns():
    return "opentool-jobs"


def get_api_v1(path: str):
    return f"{SERVICE_API_PREFIX}/{SERVICE_API_VERSION}/{path}"


def get_response(code: int, status: str, msg: str, data: dict = None):
    from fastapi.responses import JSONResponse

    return JSONResponse(
        content={
            "status": status,
            "msg": msg,
            "data": data,
        },
        status_code=code,
    )


def save_form_json(form: dict):
    if form:
        form_json = None
        try:
            form_json = json.dumps(form, indent=2, ensure_ascii=False)
        except Exception as err:
            return "", err

        tmp_file_path = Path(f"/tmp/{get_random_str(16)}.json")
        tmp_file_path.write_text(form_json)
        return tmp_file_path, None
    return None, "request missed form data"


if not IS_DEBUG_MODE:
    app = FastAPI(openapi_url=None)
else:
    app = FastAPI()


class ValidateAPIRequest(BaseModel):
    form: dict
    sub_model: str


class CallAPIRequest(BaseModel):
    form: dict
    sub_model: str


@app.get("/healthz")
async def healthz():
    return "ok"


def call_model_runner(models, sub_model, form, validate_only=True, **origin_kwargs):
    tmp_file_path, err = save_form_json(form)
    if err != None:
        return err

    try:
        error_handler = ErrHandler()

        if "exception_handler" in origin_kwargs:
            del origin_kwargs["exception_handler"]

        if type(models) == dict:
            current_models = {}
            for key, model in models.items():
                current_models[key] = model
                if validate_only and hasattr(model, "runner_func"):
                    model.runner_func = VALIDATE_ONLY_RUNNER

            f = to_runner_sp(
                **origin_kwargs,
                subparsers=current_models,
                exception_handler=error_handler,
            )
            f([sub_model, "--json-config", str(tmp_file_path)])

        else:
            if validate_only and ("runner_func" in origin_kwargs):
                origin_kwargs["runner_func"] = VALIDATE_ONLY_RUNNER
            origin_to_runner(
                **origin_kwargs,
                cls=models,
                exception_handler=error_handler,
            )(["--json-config", str(tmp_file_path)])

        errors = error_handler.get_errors()
        if errors:
            return errors
        else:
            return None
    except Exception as err:
        return err


def create_json_config_configmap(job_name: str, form_json_file_name: str, form: dict):
    try:
        configmap = client.V1ConfigMap(
            api_version="v1",
            kind="ConfigMap",
            metadata=client.V1ObjectMeta(name=job_name),
            data={form_json_file_name: json.dumps(form, indent=2, ensure_ascii=False)},
        )
        core_api = client.CoreV1Api()
        cm = core_api.create_namespaced_config_map(
            namespace=get_opentool_jobs_ns(), body=configmap
        )
        if not cm:
            raise Exception("create form json configmap failed")
    except Exception as err:
        return err
    return None


def create_vcjob(
    job_name: str,
    sub_model: str,
    form_json_file_path: str,
    form_json_file_name: str,
    job_path: str,
    image_name: str,
    entry_path: str,
    request_cpu_cores: str,
    request_memory: str,
    limit_cpu_cores: str,
    limit_memory: str,
):
    try:
        crd_instance = client.CustomObjectsApi()
        vcjob_res = crd_instance.create_namespaced_custom_object(
            group="batch.volcano.sh",
            version="v1alpha1",
            namespace=get_opentool_jobs_ns(),
            plural="jobs",
            body={
                "apiVersion": "batch.volcano.sh/v1alpha1",
                "kind": "Job",
                "metadata": {
                    "name": job_name,
                    "namespace": get_opentool_jobs_ns(),
                },
                "spec": {
                    "minAvailable": 1,
                    "schedulerName": "volcano",
                    "queue": "opentool-job-queue",
                    "policies": [
                        {
                            "event": "PodEvicted",
                            "action": "RestartJob",
                        }
                    ],
                    "tasks": [
                        {
                            "replicas": 1,
                            "name": "app",
                            "policies": [
                                {"event": "TaskCompleted", "action": "CompleteJob"}
                            ],
                            "template": {
                                "spec": {
                                    "restartPolicy": "Never",
                                    "activeDeadlineSeconds": 3600,
                                    "volumes": [
                                        {
                                            "name": "shared-data-volume",
                                            "persistentVolumeClaim": {
                                                "claimName": "jfs-prod"
                                            },
                                        },
                                        {
                                            "name": "configmap-volume",
                                            "configMap": {"name": job_name},
                                        },
                                    ],
                                    "initContainers": [
                                        {
                                            "command": ["/bin/sh", "-c", "--"],
                                            "args": ["mkdir -p " + str(job_path)],
                                            "image": "busybox",
                                            "name": "init",
                                            "volumeMounts": [
                                                {
                                                    "mountPath": TMP_PATH_PREFIX,
                                                    "name": "shared-data-volume",
                                                    "subPath": TMP_PATH_PREFIX.lstrip(
                                                        "/"
                                                    ),
                                                }
                                            ],
                                        }
                                    ],
                                    "containers": [
                                        {
                                            "command": ["/bin/sh", "-c", "--"],
                                            "args": ["sleep 3600"]
                                            if IS_DEBUG_MODE
                                            else [
                                                f"python {entry_path} {sub_model} --json-config {form_json_file_path}"
                                            ],
                                            "image": image_name,
                                            "name": "app",
                                            "volumeMounts": [
                                                {
                                                    "mountPath": form_json_file_path,
                                                    "name": "configmap-volume",
                                                    "subPath": form_json_file_name,
                                                },
                                                {
                                                    "mountPath": TMP_PATH_PREFIX,
                                                    "name": "shared-data-volume",
                                                    "subPath": job_path.lstrip("/"),
                                                },
                                            ],
                                            "resources": {
                                                "requests": {
                                                    "cpu": request_cpu_cores,
                                                    "memory": request_memory,
                                                },
                                                "limits": {
                                                    "cpu": limit_cpu_cores,
                                                    "memory": limit_memory,
                                                },
                                            },
                                        }
                                    ],
                                }
                            },
                        }
                    ],
                },
            },
        )
        if not vcjob_res:
            raise Exception("create vcjob failed")
    except Exception as err:
        current_err = err
        if hasattr(err, "body"):
            current_err = err.body
        return current_err


def api_server(entry_path: Path, models, origin_kwargs=None):
    application_name = (
        os.getenv("APPLICATION_NAME") if not IS_DEBUG_MODE else "test-tool-1"
    )
    version_name = os.getenv("VERSION_NAME") if not IS_DEBUG_MODE else "test-tool-1-v-1"
    if not application_name:
        raise Exception(
            f"start launching sdk service failed: APPLICATION_NAME not found"
        )
    if not version_name:
        raise Exception(f"start launching sdk service failed: VERSION_NAME not found")
    image_name = os.getenv("IMAGE_NAME") if not IS_DEBUG_MODE else "busybox"
    entry_path = os.getenv("ENTRY_PATH") or str(entry_path)
    if not image_name or not entry_path:
        raise Exception(
            f"start launching sdk service failed: IMAGE_NAME or ENTRY_PATH not found"
        )
    max_cpu, max_memory = get_max_core_and_memory_from_cluster()

    @app.post(get_api_v1("validate"))
    async def validate(request: ValidateAPIRequest):
        form = request.form
        sub_model = request.sub_model

        err = call_model_runner(
            models, sub_model, form, validate_only=True, **origin_kwargs
        )
        if err != None:
            return get_response(
                HTTP_STATUS.HTTP_400_BAD_REQUEST, SERVICE_STATUS_ERROR, err
            )
        return get_response(HTTP_STATUS.HTTP_200_OK, SERVICE_STATUS_SUCCESS, None)

    @app.post(get_api_v1("call"))
    async def call(request: CallAPIRequest):
        form = request.form
        sub_model = request.sub_model

        err = call_model_runner(
            models, sub_model, form, validate_only=False, **origin_kwargs
        )
        if err != None:
            return get_response(
                HTTP_STATUS.HTTP_400_BAD_REQUEST, SERVICE_STATUS_ERROR, err
            )
        return get_response(HTTP_STATUS.HTTP_200_OK, SERVICE_STATUS_SUCCESS, None)

    def get_job_resources():
        request_cpu_cores = os.getenv("JOB_REQUEST_CPU_CORES") or 1
        request_memory = os.getenv("JOB_REQUEST_MEMORY") or "1Gi"
        limit_cpu_cores = os.getenv("JOB_LIMIT_CPU_CORES") or max_cpu
        limit_memory = os.getenv("JOB_LIMIT_MEMORY") or f"{max_memory}Gi"
        if compare_cpu_cores(
            str(request_cpu_cores), str(limit_cpu_cores)
        ) or compare_memory(str(request_memory), str(limit_memory)):
            return None, None, None, None, "request resource is greater than limit"
        return request_cpu_cores, request_memory, limit_cpu_cores, limit_memory, None

    def get_names(
        application_name: str,
        version_name: str,
        sub_model: str,
        job_name: Optional[str] = None,
    ):
        current_job_name = (
            f"{application_name}-{version_name}-{sub_model}-{get_random_str(10).lower()}"
            if job_name == None
            else job_name
        )
        current_form_json_file_name = f"{sub_model}_{get_random_str(10)}.json"
        return current_job_name, current_form_json_file_name

    def get_paths(
        application_name: str,
        version_name: str,
        job_name: str,
        form_json_file_name: str,
    ):
        # shared volumn path
        job_path = f"/tmp/uploaded_files/{application_name}/{version_name}/{job_name}"
        # container job path
        form_json_file_path = f"{TMP_PATH_PREFIX}/{form_json_file_name}"
        return job_path, form_json_file_path

    def _create_job(request: CallAPIRequest, job_name: Optional[str]):
        form = request.form
        sub_model = request.sub_model
        (
            request_cpu_cores,
            request_memory,
            limit_cpu_cores,
            limit_memory,
            err,
        ) = get_job_resources()
        if err != None:
            return get_response(
                HTTP_STATUS.HTTP_500_INTERNAL_SERVER_ERROR,
                SERVICE_STATUS_ERROR,
                f"get job resources failed: {err}",
            )
        try:
            job_name, form_json_file_name = get_names(
                application_name, version_name, sub_model, job_name
            )
            job_path, form_json_file_path = get_paths(
                application_name, version_name, job_name, form_json_file_name
            )

            err = create_json_config_configmap(job_name, form_json_file_name, form)
            if err != None:
                return get_response(
                    HTTP_STATUS.HTTP_500_INTERNAL_SERVER_ERROR,
                    SERVICE_STATUS_ERROR,
                    err,
                )

            err = call_model_runner(
                models, sub_model, form, validate_only=True, **origin_kwargs
            )

            if err != None:
                return get_response(
                    HTTP_STATUS.HTTP_400_BAD_REQUEST, SERVICE_STATUS_ERROR, err
                )

            err = create_vcjob(
                job_name,
                sub_model,
                application_name,
                version_name,
                form_json_file_path,
                form_json_file_name,
                job_path,
                image_name,
                entry_path,
                request_cpu_cores,
                request_memory,
                limit_cpu_cores,
                limit_memory,
            )
            if err != None:
                return get_response(
                    HTTP_STATUS.HTTP_500_INTERNAL_SERVER_ERROR,
                    SERVICE_STATUS_ERROR,
                    f"call failed: {current_err}",
                )
            return get_response(
                HTTP_STATUS.HTTP_200_OK,
                SERVICE_STATUS_SUCCESS,
                "call succedd",
                {"job_id": job_name},
            )

        except Exception as err:
            current_err = err
            if hasattr(err, "body"):
                current_err = err.body
            return get_response(
                HTTP_STATUS.HTTP_500_INTERNAL_SERVER_ERROR,
                SERVICE_STATUS_ERROR,
                f"call failed: {current_err}",
            )

    @app.post(get_api_v1("job/{job_id}"))
    async def create_job(job_id: str, request: CallAPIRequest):
        return _create_job(request=request, job_name=job_id)

    @app.post(get_api_v1("job"))
    async def create_job(request: CallAPIRequest):
        return _create_job(request=request, job_name=None)

    # TODO || BUGFIX: 如果创建了一个 job 并且 error 了, 此时调用查询状态或者删除的 api 的话有几率会多创建出一个 pod
    @app.get(get_api_v1("job/{job_id}"))
    async def status(job_id: str):
        try:
            crd_instance = client.CustomObjectsApi()
            vcjob_res = crd_instance.get_namespaced_custom_object_status(
                group="batch.volcano.sh",
                version="v1alpha1",
                namespace=get_opentool_jobs_ns(),
                plural="jobs",
                name=job_id,
            )

            if not vcjob_res:
                return get_response(
                    HTTP_STATUS.HTTP_400_BAD_REQUEST,
                    SERVICE_STATUS_ERROR,
                    f"Job({job_id}) not found",
                )

            job_phase = vcjob_res.get("status", {}).get("state", {}).get("phase", "")
            if not job_phase:
                return get_response(
                    HTTP_STATUS.HTTP_200_OK,
                    SERVICE_STATUS_SUCCESS,
                    "Not Ready",
                    {"status": "unknown"},
                )

            return get_response(
                HTTP_STATUS.HTTP_200_OK,
                SERVICE_STATUS_SUCCESS,
                "Get Job Status Succeed",
                {"status": job_phase},
            )
        except Exception as err:
            current_err = err
            if hasattr(err, "body"):
                current_err = err.body
            return get_response(
                HTTP_STATUS.HTTP_500_INTERNAL_SERVER_ERROR,
                SERVICE_STATUS_ERROR,
                f"get job({job_id}) status failed: {current_err}",
            )

    @app.delete(get_api_v1("job/{job_id}"))
    async def cancel(job_id: str):
        try:
            crd_instance = client.CustomObjectsApi()
            body = client.V1DeleteOptions(propagation_policy="Background")
            vcjob_res = crd_instance.delete_namespaced_custom_object(
                group="batch.volcano.sh",
                version="v1alpha1",
                namespace=get_opentool_jobs_ns(),
                plural="jobs",
                name=job_id,
                body=body,
            )
            core_api = client.CoreV1Api()
            cm = core_api.delete_namespaced_config_map(
                namespace=get_opentool_jobs_ns(), name=job_id, body=body
            )
            return get_response(
                HTTP_STATUS.HTTP_200_OK,
                SERVICE_STATUS_SUCCESS,
                f"Job({job_id}) deletion succeed",
            )

        except Exception as err:
            current_err = err
            if hasattr(err, "body"):
                current_err = err.body
            return get_response(
                HTTP_STATUS.HTTP_500_INTERNAL_SERVER_ERROR,
                SERVICE_STATUS_ERROR,
                f"Job({job_id}) deletion failed, {current_err}",
            )
