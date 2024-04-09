import argparse
import inspect
import json
import os
import sys
import typing as T
from pathlib import Path
from typing import Callable as F

from dp.launching.typing.basic import BaseModel

from pydantic_cli import (
    EpilogueHandlerType,
    ExceptionHandlerType,
    M,
    PrologueHandlerType,
    SubParser,
    default_epilogue_handler,
    default_exception_handler,
    default_minimal_exception_handler,
    default_prologue_handler,
)
from pydantic_cli import run_sp_and_exit as origin_run_sp_and_exit
from pydantic_cli import to_runner as origin_to_runner


__all__ = [
    "to_runner",
    "default_minimal_exception_handler",
    "SubParser",
    "run_sp_and_exit",
]

START_API_SERVER_CONFIG = "--start-api-server"


SERVICE_START_CONFIG = "start-service"
SERVICE_API_PREFIX = "/api"
SERVICE_API_VERSION = "v1"
SERVICE_STATUS_ERROR = "error"
SERVICE_STATUS_SUCCESS = "success"


def traverse(key, _args, target_type, cb):
    if (
        isinstance(_args, list)
        or isinstance(_args, T.Tuple)
        or isinstance(_args, tuple)
        or isinstance(_args, T.List)
    ):
        for arg in _args:
            traverse(key, arg, target_type, cb)
    elif isinstance(_args, dict):
        for _key, arg in _args.items():
            traverse(_key, arg, target_type, cb)
    elif isinstance(_args, target_type):
        isinstance(cb, T.Callable) and cb(key, _args)


def print_extra_help(entry):
    print(
        f"""usage: {entry} [-h] [--gen_schema | --gen-schema] [-o OUTPUT]

optional arguments:
  -h, --help                          Show this help message and exit
  --gen_schema, --gen-schema          Generate a schema json file.
  {START_API_SERVER_CONFIG}                  Start launching api server.
  -o OUTPUT, --output OUTPUT          Schema json file output path.
    """
    )


def get_schema_properties(model) -> dict:
    return model.schema(by_alias=True).get("properties", {})


def get_schema_references(model) -> dict:
    return model.schema(by_alias=True).get("definitions", {})


def get_required_properties(model) -> dict:
    return model.schema(by_alias=True).get("required", [])


def get_internal_meta(model) -> dict:
    return model.schema(by_alias=True).get("__internal_meta__", {})


def get_doc(model):
    try:
        doc = inspect.getdoc(model)
        if doc:
            return doc
        class_file = inspect.getfile(model)
        caller_path = Path(os.path.abspath(class_file))
        if not caller_path.exists():
            return ""
        scope = {}
        scope["__name__"] = ""
        with open(caller_path, "r") as f:
            exec(f.read(), scope, scope)
            doc = scope.get("__doc__", "")
            return doc
    except Exception as _:
        return ""


def start_api_server(entry_path: Path, models, origin_kwargs=None):
    try:
        import uvicorn
        from dp.launching.cli.api.persistent_service import app, api_server

        api_server(entry_path, models, origin_kwargs)
        uvicorn.run(app, host="0.0.0.0", port=50005)

    except Exception as err:
        raise Exception(f"start launching sdk service falied: {err}")


def get_schema(model, type: str) -> dict:
    return {
        "model_type": type,
        "documentation": get_doc(model),
        "description": model.description if hasattr(model, "description") else "",
        "schema_properties": get_schema_properties(model),
        "schema_references": get_schema_references(model),
        "required_properties": get_required_properties(model),
        "__internal_meta__": get_internal_meta(model),
    }


def get_internal_schemas_output_path(name: str, output_path: str):
    path = Path(output_path)
    path.mkdir(exist_ok=True, parents=True)
    path = path / (name + ".json")
    return path


def gen_model_schema(model, output_path, name=None, type=""):
    res = get_schema(model, type)
    path = get_internal_schemas_output_path(name or model.__name__, output_path)
    path.write_text(json.dumps(res, indent=2, ensure_ascii=False))


class to_runner(origin_to_runner):
    def __init__(
        self,
        cls: T.Type[M],
        runner_func: F[[M], int],
        description: T.Optional[str] = None,
        version: T.Optional[str] = None,
        exception_handler: ExceptionHandlerType = default_exception_handler,
        prologue_handler: PrologueHandlerType = default_prologue_handler,
        epilogue_handler: EpilogueHandlerType = default_epilogue_handler,
        outputOptions: T.Type[M] = None,
    ):
        self.model = cls
        self.runner_func = runner_func
        self.description = description
        self.version = version
        self.outputOptions = outputOptions
        super().__init__(
            cls,
            runner_func,
            description,
            version,
            exception_handler,
            prologue_handler,
            epilogue_handler,
        )

    def __call__(self, args: T.List[str]) -> int:
        python_entry_path = Path(sys.argv[0])
        if not python_entry_path.exists():
            raise Exception(f"python entry path {python_entry_path} not exists")
        if len(sys.argv) == 1:
            print_extra_help(sys.argv[0])
        for item in args:
            if item == "-h" or item == "--help":
                print_extra_help(sys.argv[0])
                return super().__call__(args)
            elif item == "--gen_schema":
                parser = argparse.ArgumentParser("Launching-Schema-Gen")
                parser.add_argument(
                    "--gen_schema",
                    action="store_true",
                    default=False,
                    help="Generate a schema json file.",
                )
                parser.add_argument(
                    "-o",
                    "--output",
                    type=str,
                    default="generated_schemas",
                    help="Schema json file output path.",
                )
                gen_schema_args = parser.parse_args()
                return self.gen_schema(gen_schema_args.output)
            elif item == "--gen-schema":
                parser = argparse.ArgumentParser("Launching-Schema-Gen")
                parser.add_argument(
                    "--gen-schema",
                    action="store_true",
                    default=False,
                    help="Generate a schema json file.",
                )
                parser.add_argument(
                    "-o",
                    "--output",
                    type=str,
                    default="generated_schemas",
                    help="Schema json file output path.",
                )
                gen_schema_args = parser.parse_args()
                return self.gen_schema(gen_schema_args.output)
            elif item == START_API_SERVER_CONFIG:
                return start_api_server(
                    python_entry_path,
                    self.model,
                    {
                        "runner_func": self.runner_func,
                        "description": self.description,
                        "version": self.version,
                    },
                )

        return sys.exit(super().__call__(args))

    def gen_schema(self, output_path):
        try:
            if hasattr(self, "model"):
                fileName = self.model.__name__ + "_inputs"
                gen_model_schema(self.model, output_path, fileName, "single")
                print(
                    f"JSONSchema describe file for {fileName} has been generated successfully to {output_path}/{fileName}.json"
                )
            if hasattr(self, "outputOptions") and self.outputOptions is not None:
                fileName = self.outputOptions.__name__ + "_inputs"
                gen_model_schema(self.outputOptions, output_path, fileName, "single")
                print(
                    f"JSONSchema describe file for {fileName} has been generated successfully to {output_path}/{fileName}.json"
                )
            print(
                f"Verify your schema at Dev Assistant https://launching.mlops.dp.tech/?request=GET%3A%2Fdeveloper_assistant"
            )
        except Exception as err:
            import traceback

            traceback.print_exc()
            print("gen schema failed: ", err)


class run_sp_and_exit:
    def __init__(self, *args, **kwargs) -> None:
        python_entry_path = Path(sys.argv[0])
        if not python_entry_path.exists():
            raise Exception(f"python entry path {python_entry_path} not exists")
        if len(sys.argv) == 1:
            print_extra_help(sys.argv[0])
        if len(sys.argv) >= 1:
            for item in sys.argv[1:]:
                if item == "-h" or item == "--help":
                    print_extra_help(sys.argv[0])
                elif item == "--gen_schema":
                    parser = argparse.ArgumentParser("Launching-Schema-Gen")
                    parser.add_argument(
                        "--gen_schema",
                        action="store_true",
                        default=False,
                        help="Generate a schema json file. Default to ./generated_schemas/",
                    )
                    parser.add_argument(
                        "-o",
                        "--output",
                        type=str,
                        default="generated_schemas",
                        help="Schema json file output path.",
                    )
                    gen_schema_args = parser.parse_args()
                    self.gen_schema(gen_schema_args.output, args, kwargs)
                    return
                elif item == "--gen-schema":
                    parser = argparse.ArgumentParser("Launching-Schema-Gen")
                    parser.add_argument(
                        "--gen-schema",
                        action="store_true",
                        default=False,
                        help="Generate a schema json file.",
                    )
                    parser.add_argument(
                        "-o",
                        "--output",
                        type=str,
                        default="generated_schemas",
                        help="Schema json file output path.",
                    )
                    gen_schema_args = parser.parse_args()
                    self.gen_schema(gen_schema_args.output, args, kwargs)
                    return
                elif item == START_API_SERVER_CONFIG:
                    models = {}

                    def __update_runner_func(key, sub_parser):
                        if hasattr(sub_parser, "runner_func"):
                            models[key] = sub_parser
                            # sub_parser.runner_func = VALIDATE_ONLY_RUNNER

                    traverse("", args, SubParser, __update_runner_func)
                    return start_api_server(python_entry_path, models, kwargs)

        if "exception_handler" not in kwargs:
            kwargs["exception_handler"] = default_minimal_exception_handler
        origin_run_sp_and_exit(*args, **kwargs)

    def gen_schema(self, output, args, kwargs):
        self.models = self.__get_models({"tmp1": args, "tmp2": kwargs})
        try:
            for name, model in self.models.items():
                gen_model_schema(model, output, name, "multiple")
                print(
                    f"JSONSchema describe file for {model.__name__} has been generated successfully to {output}/{name}.json"
                )
            print(
                f"Verify your schema at Dev Assistant https://launching.mlops.dp.tech/?request=GET%3A%2Fdeveloper_assistant"
            )
        except Exception as err:
            print("gen schemas failed: ", err)

    def __get_models(self, origin: dict):
        res = {}
        for key, value in origin.items():
            if isinstance(value, dict):
                res.update(self.__get_models(value))
            elif isinstance(value, list) or isinstance(value, tuple):
                for i in value:
                    res.update(self.__get_models(i))
            elif isinstance(value, BaseModel):
                res.update({value.__name__: value})
            elif isinstance(value, SubParser):
                value.model_class.description = value.description or ""
                value.documentation = get_doc(value.model_class)
                res.update({key+"_inputs": value.model_class})
                # 添加outputOptions
                if value.outputOptions:
                    res.update({key+"_outputs": value.outputOptions})
        return res
