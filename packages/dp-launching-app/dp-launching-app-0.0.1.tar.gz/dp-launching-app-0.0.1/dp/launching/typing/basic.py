import base64
from typing import Union, Optional, List, Dict, Tuple, Set, Any, Literal
from datetime import datetime, date
from enum import Enum

from pydantic import (
    BaseModel as BBaseModel,
    Field,
    ValidationError,  # noqa
    parse_obj_as,  # noqa
    json,  # noqa
    parse_raw_as,  # noqa
    validator,  # noqa
    root_validator,  # noqa
)
from pydantic.fields import FieldInfo, ModelField
from pydantic_cli import DefaultConfig
from pydantic.main import model_schema

__all__ = [
    "BaseModel",
    "Field",
    "parse_obj_as",
    "ValidationError",
    "json",
    "parse_raw_as",
    "Union",
    "Optional",
    "List",
    "Dict",
    "Tuple",
    "Set",
    "Enum",
    "Literal",
    "Int",
    "String",
    "Float",
    "DateTime",
    "Date",
    "Boolean",
    "GenUUID",
    "validator",
    "root_validator",
    "MinMaxRange",
]

Int = int
String = str
Float = float
DateTime = datetime
Boolean = bool
Date = date

# __INTERNAL_KEY__ = 'TYPING_INTERNAL_PREFIX_' + \
#     ''.join(random.choices(string.ascii_letters + string.digits, k=10))

__INTERNAL_KEY__ = "TYPING_INTERNAL_PREFIX_TYPING"


def get_internal_key():
    return __INTERNAL_KEY__


class BaseModel(BBaseModel):
    # __id = None
    __fields = None
    __internal_meta = {}
    __hooks = {"field_info_extra": []}

    @classmethod
    def __get_id__(cls):
        return cls.__qualname__ or cls.__name__

    @classmethod
    def __add_field_info_extra_hook__(cls, hook):
        if isinstance(hook, function):
            cls.__hooks["field_info_extra"].append(hook)

    @classmethod
    def __add_meta_id__(cls):
        for field in cls.__fields__.values():
            if isinstance(field, ModelField):
                field.field_info.extra = {
                    **field.field_info.extra,
                    "__current": f"field_{field.name}",
                    "__parent": cls.__get_id__(),
                }
        return cls.__fields__

    @classmethod
    def __get_fields__(cls):
        if not cls.__fields:
            cls.__fields = cls.__add_meta_id__()
        return cls.__fields

    @classmethod
    def __get_schema_json__(cls, schema):
        import json
        from json import JSONEncoder

        class CustomEncoder(JSONEncoder):
            def setEncoder(self, obj):
                return list(obj)

            def default(self, obj):
                from datetime import date
                from datetime import datetime

                if isinstance(obj, datetime):
                    return obj.isoformat()
                elif isinstance(obj, date):
                    return obj.isoformat()
                elif isinstance(obj, set):
                    return self.setEncoder(obj)
                elif hasattr(obj, "__get_field_schema__"):
                    return obj.__get_field_schema__()
                return super().default(obj)

        return json.dumps(schema, cls=CustomEncoder, indent=2, ensure_ascii=False)

    @classmethod
    def schema(cls, *args, **kwargs):
        tmp_names = {}
        for base in [cls] + list(cls.__bases__):
            if isinstance(base, type) and issubclass(base, BaseModel):
                for field in base.__fields__.values():
                    if isinstance(field, ModelField):
                        # 这里不知道为啥, 如果直接用 field.field_info.extra.update 的方式去改
                        # 就会不生效
                        if "__current" not in field.field_info.extra:
                            tmp_names[field.name] = {"__current": f"field_{field.name}"}
                        if "__parent" not in field.field_info.extra:
                            tmp_names[field.name] = {
                                **tmp_names[field.name],
                                "__parent": base.__get_id__(),
                            }
                cls.__internal_meta[base.__get_id__()] = base.origin_schema()
                if hasattr(base, "__get_group_info__"):
                    cls.__internal_meta[base.__get_id__()][
                        "group"
                    ] = base.__get_group_info__()

        for field in cls.__fields__.values():
            if isinstance(field, ModelField):
                if "__current" not in field.field_info.extra:
                    field.field_info.extra.update(
                        {"__current": tmp_names[field.name]["__current"]}
                    )
                if "__parent" not in field.field_info.extra:
                    field.field_info.extra.update(
                        {"__parent": tmp_names[field.name]["__parent"]}
                    )

        res = model_schema(cls, *args, **kwargs)
        import json

        if get_internal_key() in res["properties"]:
            del res["properties"][get_internal_key()]
        res = json.loads(cls.__get_schema_json__(res))
        # res = json.loads(json.dumps(res))
        cls_internal_meta = cls.__internal_meta
        res["__internal_meta__"] = cls_internal_meta
        res = json.loads(cls.__get_schema_json__(res))
        return res

    @classmethod
    def origin_schema(cls, *args, **kwargs):
        return super().schema(*args, **kwargs)

    class Config(DefaultConfig):
        CLI_JSON_ENABLE = True


class GenUUID(str):
    def get_value(self):
        return str(self)

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(format="gen_uuid", scope="executor")

    @classmethod
    def __get_validators__(cls) -> Any:
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> "GenUUID":
        if isinstance(value, GenUUID):
            return value
        elif isinstance(value, str):
            return GenUUID(value)
        elif isinstance(value, (bytes, bytearray, memoryview)):
            return GenUUID(base64.b64encode(value).decode())
        else:
            raise Exception("Wrong type")


class MinMaxRange(str):
    def get_value(self) -> Tuple[float, float]:
        _min, _max = map(float, str(self).split(","))
        return _min, _max

    @property
    def lower(self) -> float:
        return self.get_value()[0]

    @property
    def upper(self) -> float:
        return self.get_value()[1]

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(
            format="min_max_range",
            render_hint="float",
        )

    @classmethod
    def __get_validators__(cls) -> Any:
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> "MinMaxRange":
        if isinstance(value, MinMaxRange):
            return value
        elif isinstance(value, (tuple, list)) and len(value) == 2:
            return MinMaxRange(f"{value[0]},{value[1]}")
        elif isinstance(value, str):
            return MinMaxRange(value)
        elif isinstance(value, (bytes, bytearray, memoryview)):
            return MinMaxRange(base64.b64encode(value).decode())
        else:
            raise Exception(f"MinMaxRange Wrong type: {type(value)}")
