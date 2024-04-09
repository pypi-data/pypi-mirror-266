import base64
from typing import Any, Dict

__all__ = [
    "BohriumJobType",
    "BohriumMachineType",
    "BohriumProjectId",
    "BohriumPlatform",
    "BohriumUsername",
    "BohriumTicket",
    "BohriumImage",
    "BohriumInstanceType",
    "BohriumStreamEndpoint",
    "BohriumJobID",
]


class BohriumUsername(str):
    def get_value(self):
        return str(self)

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(format="bohrium_username", scope="executor")

    @classmethod
    def __get_validators__(cls) -> Any:
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> "BohriumUsername":
        if isinstance(value, BohriumUsername):
            return value
        elif isinstance(value, str):
            return BohriumUsername(value)
        elif isinstance(value, (bytes, bytearray, memoryview)):
            return BohriumUsername(base64.b64encode(value).decode())
        else:
            raise Exception(f"BohriumUsername Wrong type: {type(value)}")


class BohriumTicket(str):
    def get_value(self):
        return str(self)

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(format="bohrium_ticket", scope="executor")

    @classmethod
    def __get_validators__(cls) -> Any:
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> "BohriumTicket":
        if isinstance(value, BohriumTicket):
            return value
        elif isinstance(value, str):
            return BohriumTicket(value)
        elif isinstance(value, (bytes, bytearray, memoryview)):
            return BohriumTicket(base64.b64encode(value).decode())
        else:
            raise Exception(f"BohriumTicket Wrong type: {type(value)}")


class BohriumProjectId(str):
    def get_value(self):
        return str(self)

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(format="bohrium_project_id", scope="executor")

    @classmethod
    def __get_validators__(cls) -> Any:
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> "BohriumProjectId":
        if isinstance(value, BohriumProjectId):
            return value
        elif isinstance(value, str):
            return BohriumProjectId(value)
        elif isinstance(value, (bytes, bytearray, memoryview)):
            return BohriumProjectId(base64.b64encode(value).decode())
        else:
            raise Exception(f"BohriumProjectId Wrong type: {type(value)}")


class BohriumImage(str):
    def get_value(self):
        return str(self)

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(format="bohrium_image", scope="executor")

    @classmethod
    def __get_validators__(cls) -> Any:
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> "BohriumImage":
        if isinstance(value, BohriumImage):
            return value
        elif isinstance(value, str):
            return BohriumImage(value)
        elif isinstance(value, (bytes, bytearray, memoryview)):
            return BohriumImage(base64.b64encode(value).decode())
        else:
            raise Exception(f"BohriumImage Wrong type: {type(value)}")


class BohriumJobType(str):
    INDICATE: "BohriumJobType"
    CONTAINER: "BohriumJobType"

    def __get_default_options__(self):
        return (
            self.CONTAINER,
            self.INDICATE,
        )

    def get_value(self):
        return str(self)

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(format="bohrium_job_type", scope="executor")

    @classmethod
    def __get_validators__(cls) -> Any:
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> "BohriumJobType":
        if isinstance(value, BohriumJobType):
            return value
        elif isinstance(value, str):
            return BohriumJobType(value)
        elif isinstance(value, (bytes, bytearray, memoryview)):
            return BohriumJobType(base64.b64encode(value).decode())
        else:
            raise Exception(f"BohriumJobType Wrong type: {type(value)}")


BohriumJobType.INDICATE = BohriumJobType("indicate")
BohriumJobType.CONTAINER = BohriumJobType("container")


class BohriumMachineType(str):
    C2_M8_CPU: "BohriumMachineType"
    C4_M16_CPU: "BohriumMachineType"
    C8_M32_CPU: "BohriumMachineType"
    C8_M31_1__NVIDIA_T4: "BohriumMachineType"
    C8_M32_1__NVIDIA_V100: "BohriumMachineType"
    C8_M60_1__NVIDIA_P100: "BohriumMachineType"

    def __get_default_options__(self):
        return (
            self.C2_M8_CPU,
            self.C4_M16_CPU,
            self.C8_M32_CPU,
            self.C8_M31_1__NVIDIA_T4,
            self.C8_M32_1__NVIDIA_V100,
            self.C8_M60_1__NVIDIA_P100,
        )

    def get_value(self):
        return str(self)

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(format="bohrium_machine_type", scope="executor")

    @classmethod
    def __get_validators__(cls) -> Any:
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> "BohriumMachineType":
        if isinstance(value, BohriumMachineType):
            return value
        elif isinstance(value, str):
            return BohriumMachineType(value)
        elif isinstance(value, (bytes, bytearray, memoryview)):
            return BohriumMachineType(base64.b64encode(value).decode())
        else:
            raise Exception(f"BohriumMachineType Wrong type: {type(value)}")


BohriumMachineType.C2_M8_CPU = BohriumMachineType("c2_m8_cpu")
BohriumMachineType.C4_M16_CPU = BohriumMachineType("c4_m16_cpu")
BohriumMachineType.C8_M32_CPU = BohriumMachineType("c8_m32_cpu")
BohriumMachineType.C8_M31_1__NVIDIA_T4 = BohriumMachineType("c8_m31_1 * NVIDIA T4")
BohriumMachineType.C8_M32_1__NVIDIA_V100 = BohriumMachineType("c8_m32_1 * NVIDIA V100")
BohriumMachineType.C8_M60_1__NVIDIA_P100 = BohriumMachineType("c8_m60_1 * NVIDIA P100")


class BohriumPlatform(str):
    ALI: "BohriumPlatform"
    PARATERA: "BohriumPlatform"

    def __get_default_options__(self):
        return (self.ALI,)

    def get_value(self):
        return str(self)

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(format="bohrium_platform", scope="executor")

    @classmethod
    def __get_validators__(cls) -> Any:
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> "BohriumPlatform":
        if isinstance(value, BohriumPlatform):
            return value
        elif isinstance(value, str):
            return BohriumPlatform(value)
        elif isinstance(value, (bytes, bytearray, memoryview)):
            return BohriumPlatform(base64.b64encode(value).decode())
        else:
            raise Exception(f"BohriumPlatform Wrong type: {type(value)}")


BohriumPlatform.ALI = BohriumPlatform("ali")
BohriumPlatform.PARATERA = BohriumPlatform("paratera")


class BohriumInstanceType(str):
    ON_DEMAND: "BohriumInstanceType"
    SPOT: "BohriumInstanceType"

    def __get_default_options__(self):
        return (
            self.SPOT,
            self.ON_DEMAND,
        )

    def get_value(self):
        return str(self)

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(format="bohrium_instance_type", scope="executor")

    @classmethod
    def __get_validators__(cls) -> Any:
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> "BohriumInstanceType":
        if isinstance(value, BohriumInstanceType):
            return value
        elif isinstance(value, str):
            return BohriumInstanceType(value)
        else:
            raise Exception(f"BohriumInstanceType Wrong type: {type(value)}")


BohriumInstanceType.ON_DEMAND = BohriumInstanceType("On Demand")
BohriumInstanceType.SPOT = BohriumInstanceType("SPOT")


class BohriumJobID(str):
    def get_value(self):
        return str(self)

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(format="bohrium_job_id", scope="executor")

    @classmethod
    def __get_validators__(cls) -> Any:
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> "BohriumJobID":
        if isinstance(value, BohriumJobID):
            return value
        elif isinstance(value, str):
            return BohriumJobID(value)
        elif isinstance(value, (bytes, bytearray, memoryview)):
            return BohriumJobID(base64.b64encode(value).decode())
        else:
            raise Exception(f"BohriumJobID Wrong type: {type(value)}")


class BohriumStreamEndpoint(str):
    def get_value(self):
        return str(self)

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(format="bohrium_stream_endpoint", scope="executor")

    @classmethod
    def __get_validators__(cls) -> Any:
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> "BohriumStreamEndpoint":
        if isinstance(value, BohriumStreamEndpoint):
            return value
        elif isinstance(value, str):
            return BohriumStreamEndpoint(value)
        elif isinstance(value, (bytes, bytearray, memoryview)):
            return BohriumStreamEndpoint(base64.b64encode(value).decode())
        else:
            raise Exception(f"BohriumStreamEndpoint Wrong type: {type(value)}")
