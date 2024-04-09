import base64
from typing import Any, Dict

__all__ = [
    "DflowArgoAPIServer",
    "DflowK8sAPIServer",
    "DflowAccessToken",
    "DflowStorageEndpoint",
    "DflowStorageRepository",
    "DflowLabels"
]


class DflowArgoAPIServer(str):
    def get_value(self):
        return str(self)

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(format="dflow_argo_apiserver", scope="executor")

    @classmethod
    def __get_validators__(cls) -> Any:
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> "DflowArgoAPIServer":
        if isinstance(value, DflowArgoAPIServer):
            return value
        elif isinstance(value, str):
            return DflowArgoAPIServer(value)
        elif isinstance(value, (bytes, bytearray, memoryview)):
            return DflowArgoAPIServer(base64.b64encode(value).decode())
        else:
            raise Exception(f"DflowArgoAPIServer Wrong type: {type(value)}")


DflowHost = DflowArgoAPIServer


class DflowK8sAPIServer(str):
    def get_value(self):
        return str(self)

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(format="dflow_k8s_apiserver", scope="executor")

    @classmethod
    def __get_validators__(cls) -> Any:
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> "DflowK8sAPIServer":
        if isinstance(value, DflowK8sAPIServer):
            return value
        elif isinstance(value, str):
            return DflowK8sAPIServer(value)
        elif isinstance(value, (bytes, bytearray, memoryview)):
            return DflowK8sAPIServer(base64.b64encode(value).decode())
        else:
            raise Exception(f"DflowK8sAPIServer Wrong type: {type(value)}")


class DflowAccessToken(str):
    def get_value(self):
        return str(self)

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(format="dflow_access_token", scope="executor")

    @classmethod
    def __get_validators__(cls) -> Any:
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> "DflowAccessToken":
        if isinstance(value, DflowAccessToken):
            return value
        elif isinstance(value, str):
            return DflowAccessToken(value)
        elif isinstance(value, (bytes, bytearray, memoryview)):
            return DflowAccessToken(base64.b64encode(value).decode())
        else:
            raise Exception(f"DflowAccessToken Wrong type: {type(value)}")


class DflowStorageEndpoint(str):
    def get_value(self):
        return str(self)

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(format="dflow_storage_endpoint", scope="executor")

    @classmethod
    def __get_validators__(cls) -> Any:
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> "DflowStorageEndpoint":
        if isinstance(value, DflowStorageEndpoint):
            return value
        elif isinstance(value, str):
            return DflowStorageEndpoint(value)
        elif isinstance(value, (bytes, bytearray, memoryview)):
            return DflowStorageEndpoint(base64.b64encode(value).decode())
        else:
            raise Exception(f"DflowStorageEndpoint Wrong type: {type(value)}")


class DflowStorageRepository(str):
    def get_value(self):
        return str(self)

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(format="dflow_storage_repository", scope="executor")

    @classmethod
    def __get_validators__(cls) -> Any:
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> "DflowStorageRepository":
        if isinstance(value, DflowStorageRepository):
            return value
        elif isinstance(value, str):
            return DflowStorageRepository(value)
        elif isinstance(value, (bytes, bytearray, memoryview)):
            return DflowStorageRepository(base64.b64encode(value).decode())
        else:
            raise Exception(f"DflowStorageRepository Wrong type: {type(value)}")


class DflowLabels(dict):
    def get_value(self) -> Dict:
        if hasattr(self, "value"):
            return self.value
        return {}

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(format="dflow_labels", scope="executor")

    @classmethod
    def __get_validators__(cls) -> Any:  # type: ignore
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> "DflowLabels":
        if isinstance(value, dict):
            f = DflowLabels(value)
            f.value = value
            return f
        else:
            raise Exception(f"DflowLabels Wrong type: {type(value)}")
