import os
import base64
import os.path
import json
from typing import Any, Dict

__all__ = [
    "InputFilePath",
    "OutputDirectory",
    "DataSet",
    "Model",
    "InputMoleculeContent",
]


class InputFilePath(str):
    def get_full_path(self) -> str:
        path = self.get_path()
        return os.path.abspath(path)

    def get_path(self) -> str:
        if hasattr(self, "path"):
            return self.path
        return ""

    def get_name(self) -> str:
        if hasattr(self, "name"):
            return self.name
        return ""

    def get_value(self) -> bytes:
        if hasattr(self, "value"):
            return self.value
        return ""

    def __str__(self):
        if hasattr(self, "path"):
            return self.get_path()
        return ""

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(format="input_file_path", scope="io")

    @classmethod
    def __get_validators__(cls) -> Any:  # type: ignore
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> "InputFilePath":
        if isinstance(value, str):
            f = InputFilePath(value)
            f.path = value
            f.value = value
            f.name = os.path.basename(value)
            return f
        elif isinstance(value, dict):
            if "content" in value:
                f = InputFilePath(value["content"])
                f.value = value["content"]
                f.path = value["content"]
                if "name" in value:
                    f.name = value["name"]
                return f
            elif "path" in value:
                f = InputFilePath(value["path"])
                f.path = value["path"]
                f.value = value["path"]
                if "name" in value:
                    f.name = value["name"]
                return f
            return None
        else:
            raise Exception(f"InputFilePath Wrong type: {type(value)}")


class OutputDirectory(str):
    def get_full_path(self) -> str:
        path = self.get_path()
        return os.path.abspath(path)

    def get_path(self) -> str:
        return self.get_value()

    def get_value(self):
        return str(self)

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(format="output_directory", scope="io")

    @classmethod
    def __get_validators__(cls) -> Any:
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> "OutputDirectory":
        if isinstance(value, OutputDirectory):
            return value
        elif isinstance(value, str):
            return OutputDirectory(value)
        elif isinstance(value, (bytes, bytearray, memoryview)):
            return OutputDirectory(base64.b64encode(value).decode())
        else:
            raise Exception(f"OutputDirectory Wrong type: {type(value)}")


class DataSet(str):
    def get_value(self) -> Dict[str, Any]:
        return json.loads(str(self))

    def get_path(self) -> str:
        return self.get_value()["path"]

    def get_subpath(self) -> str:
        return self.get_value()["subpath"]

    def get_full_path(self) -> str:
        path = self.get_path()
        return os.path.abspath(path)

    def get_urn(self) -> str:
        return self.get_value()["urn"]

    def get_name(self) -> str:
        return self.get_value().get("name")

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(format="dataset", scope="io")

    @classmethod
    def __get_validators__(cls) -> Any:
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> "DataSet":
        if isinstance(value, DataSet):
            return value
        elif isinstance(value, str):
            if os.path.exists(value):
                return DataSet(json.dumps({"path": value, "urn": value}))
            elif value.startswith(["launching+", "launching:"]):
                raise Exception("URN format only avialable online")
            value = json.loads(value)
        if isinstance(value, dict) and "path" in value and "urn" in value:
            return DataSet(json.dumps(value))
        else:
            raise Exception(f"DataSet Wrong type: {type(value)}")


class Model(str):
    def get_value(self) -> Dict[str, Any]:
        return json.loads(str(self))

    def get_path(self) -> str:
        return self.get_value()["path"]

    def get_full_path(self) -> str:
        path = self.get_path()
        return os.path.abspath(path)

    def get_urn(self) -> str:
        return self.get_value()["urn"]

    def get_subpath(self) -> str:
        return self.get_value()["subpath"]

    def get_name(self) -> str:
        return self.get_value().get("name")

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(format="model", scope="io")

    @classmethod
    def __get_validators__(cls) -> Any:
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> "Model":
        if isinstance(value, Model):
            return value
        elif isinstance(value, str):
            if os.path.exists(value):
                return DataSet(json.dumps({"path": value, "urn": value, "subpath": ""}))
            elif value.startswith(["launching+", "launching:"]):
                raise Exception("URN format only avialable online")
            value = json.loads(value)
        if isinstance(value, dict) and "path" in value and "urn" in value:
            return Model(json.dumps(value))
        else:
            raise Exception(f"Model Wrong type: {type(value)}")


class InputMoleculeContent(str):
    def get_value(self) -> str:
        return str(self)

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(format="input_molecule_content", scope="io")

    @classmethod
    def __get_validators__(cls) -> Any:
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> "InputMoleculeContent":
        if isinstance(value, InputMoleculeContent):
            return value
        elif isinstance(value, str):
            return InputMoleculeContent(value)
        else:
            raise Exception(f"InputMoleculeContent Wrong type: {type(value)}")
