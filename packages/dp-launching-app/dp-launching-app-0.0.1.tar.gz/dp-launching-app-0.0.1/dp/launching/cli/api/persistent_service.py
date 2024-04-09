import os
import json
import sys
import traceback
from pathlib import Path
from fastapi import FastAPI, status as HTTP_STATUS
from pydantic.error_wrappers import ValidationError

from dp.launching.typing.basic import BaseModel
from dp.launching.cli.utils.random import get_random_str

from pydantic_cli import to_runner_sp
from pydantic_cli import to_runner as origin_to_runner
from fastapi import Header, Body

IS_DEBUG_MODE = os.getenv("PROD_ENV") == None

TMP_PATH_PREFIX = "/tmp/uploaded_files"

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

def get_api_v1(path: str):
    return f"/{path}"


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
    # sub_model: str


@app.get("/healthz")
async def healthz():
    return "ok"


def call_model_runner(models, sub_model, data, validate_only=True, **origin_kwargs) -> dict:   
    form = json_to_list(data)
    
    try:
        error_handler = ErrHandler()

        if "exception_handler" in origin_kwargs:
            del origin_kwargs["exception_handler"]
        
        result = None # Variable to store sub_model function's return value.
         
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
           
            form = [sub_model] + form
            result = f(form)
        else:
            if validate_only and ("runner_func" in origin_kwargs):
                origin_kwargs["runner_func"] = VALIDATE_ONLY_RUNNER
            result = origin_to_runner(
                **origin_kwargs,
                cls=models,
                exception_handler=error_handler,
            )(form)

        errors = error_handler.get_errors()
        if errors:
            return {"error": errors, "data": None}
        else:
            return {"error": None, "data": result}
    except Exception as err:
        return {"error": err, "data": None}

def api_server(entry_path: Path, models, origin_kwargs=None):
    entry_path = os.getenv("ENTRY_PATH") or str(entry_path)
    if not entry_path:
        raise Exception(
            f"start launching sdk service failed: ENTRY_PATH not found"
        )

    @app.post(get_api_v1(""))
    async def call(request: dict = Body(...), x_dp_method: str = Header(None)):
        if not x_dp_method:
            return get_response(
                HTTP_STATUS.HTTP_400_BAD_REQUEST,
                SERVICE_STATUS_ERROR,
                "x-dp-method is required",
            )
        result = call_model_runner(
            models, x_dp_method, request, validate_only=False, **origin_kwargs
        )
        if result["error"] != None:
            return get_response(
                HTTP_STATUS.HTTP_400_BAD_REQUEST, SERVICE_STATUS_ERROR, result["error"]
            )
        return get_response(HTTP_STATUS.HTTP_200_OK, SERVICE_STATUS_SUCCESS, None, result["data"].dict())


def json_to_list(json_data):
    try:
        if isinstance(json_data, str):
            # 如果是字符串，先解析成字典
            data = json.loads(json_data)
        elif isinstance(json_data, dict):
            # 如果是字典，直接使用
            data = json_data
        else:
            raise ValueError("Input must be a JSON string or dictionary")

        result = []
        for key, value in data.items():
            result.extend(["--" + str(key), str(value)])
        return result
    except Exception as e:
        return "Error: {}".format(e)