from typing import Any, Type, get_args, Optional
import dict_deep
from dp.launching.typing.basic import Union, Dict, Optional, BaseModel, get_internal_key
from dp.launching.typing.addon.sysmbol import (
    BasicRelationalOperator,
    BasicLogicalOperator,
    BasicFunction,
)


class UI:
    ...


def get_wrapper(type: str) -> Type[BaseModel]:
    class _UI(UI):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self.args = args
            self.kwargs = kwargs

        def __get_field_schema__(self) -> Any:
            args = self.args
            others = getOthers(args)
            operator = getBasicRelationalOperator(args)
            left = getCurrent(args)
            ref = getRef(args)
            internal_key = get_internal_key()
            refChain = getRefChain(ref)
            return {
                "scope": "internal",
                "statements": "ui",
                "value": type,
                # "group": self.__get_group_info__(),
                "params": {
                    "ref": refChain,
                    "left": (left or ref).__get_id__() if left or ref else None,
                    "operator": operator.__get_operator_name__() if operator else None,
                    "others": others,
                },
            }

        @classmethod
        def __get_group_info__(cls) -> dict:
            return (
                cls.__group_info__
                if hasattr(cls, "__group_info__")
                else {"name": "", "desc": ""}
            )

        def __call__(self, cls) -> Any:
            args = self.args
            others = getOthers(args)
            operator = getBasicRelationalOperator(args)
            left = getCurrent(args)
            ref = getRef(args)
            internal_key = get_internal_key()
            refChain = getRefChain(ref)

            class _internal_ui_property:
                __group_info__ = None

                @classmethod
                def __set_group_info__(cls, name: str, desc: str = "") -> None:
                    cls.__group_info__ = {"name": name, "desc": desc}

                @classmethod
                def __get_group_info__(cls) -> dict:
                    return (
                        cls.__group_info__
                        if hasattr(cls, "__group_info__")
                        else {"name": "", "desc": ""}
                    )

                @classmethod
                def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
                    field_schema.update(
                        scope="internal",
                        statements="ui",
                        value=type,
                        group=cls.__get_group_info__(),
                        params={
                            "ref": refChain,
                            "left": (left or ref).__get_id__()
                            if (left or ref)
                            else None,
                            "operator": operator.__get_operator_name__()
                            if operator
                            else None,
                            "others": others,
                        },
                    )

                @classmethod
                def __get_validators__(cls) -> Any:
                    yield cls.validate

                @classmethod
                def validate(cls, value: Any) -> "_internal_ui_property":
                    return _internal_ui_property

            class _stand(_Basic_internal_ref_cls, cls):
                __annotations__ = {internal_key: Optional[_internal_ui_property]}

            _stand.__qualname__ = f"{cls.__qualname__}"
            _stand.__name__ = f"{cls.__name__}"
            _stand.current = cls
            cls._stand = _stand
            _stand.__get_fields__()

            return _stand

    return _UI


class _Basic_internal_ref_cls:
    @classmethod
    def get_current(cls):
        return cls.current


# def getUI(args: tuple) -> UI:
#     for arg in args:
#         if isinstance(arg, type) and issubclass(arg, UI):
#             return arg


def getBasicRelationalOperator(args: tuple) -> BasicRelationalOperator:
    for arg in args:
        if isinstance(arg, type) and issubclass(arg, BasicRelationalOperator):
            return arg


def getBasicLogicalOperator(args: tuple) -> BasicLogicalOperator:
    for arg in args:
        if isinstance(arg, type) and issubclass(arg, BasicLogicalOperator):
            return arg


def is_internal_cls(target: Any) -> bool:
    if not isinstance(target, type):
        return False

    if (
        not issubclass(target, BasicLogicalOperator)
        and not issubclass(target, BasicRelationalOperator)
        and not issubclass(target, BasicFunction)
        and not issubclass(target, BaseModel)
    ):
        # and not issubclass(target, UI) and
        return False
    return True


def getOthers(args: tuple) -> Optional[tuple]:
    res = []
    for arg in args:
        if not is_internal_cls(arg):
            res.append(arg)
    return tuple(res)


def getCurrent(args: tuple) -> Optional[BaseModel]:
    for arg in args:
        if isinstance(arg, type) and issubclass(arg, _Basic_internal_ref_cls):
            return arg.get_current()


def getRef(args: BaseModel) -> Optional[BaseModel]:
    for arg in args:
        if isinstance(arg, type) and issubclass(arg, BaseModel):
            return arg


def getRefChain(ref):
    if not ref or not hasattr(ref, "origin_schema"):
        return None
    if not isinstance(ref, type) or not issubclass(ref, _Basic_internal_ref_cls):
        return None
    sch = ref.origin_schema()
    parent = dict_deep.deep_get(sch, f"properties.{get_internal_key()}.params")
    return {
        "schema": sch,
        "parent": parent,
    }


Visible = get_wrapper("Visible")

Hidden = get_wrapper("Hidden")


class Group:
    def __init__(self, name: str, desc: str = "") -> None:
        self.name = name
        self.desc = desc

    # @classmethod
    # def __set_group_info__(cls, name: str, desc: str = "") -> None:
    #     cls.__group_info__ = {"name": name, "desc": desc}

    def __add_group__(self, cls) -> dict:
        _internal_ui_property = cls._stand.__annotations__[get_internal_key()]
        if get_args(_internal_ui_property):
            for u in get_args(_internal_ui_property):
                if hasattr(u, "__set_group_info__"):
                    u.__set_group_info__(self.name, self.desc)
        elif hasattr(_internal_ui_property, "__set_group_info__"):
            _internal_ui_property.__set_group_info__(self.name, self.desc)
        return cls._stand

    def __call__(self, cls) -> Any:
        if hasattr(cls, "_stand"):
            return self.__add_group__(cls)
        else:
            cls = Visible(None, None, None)(cls)
            return self.__add_group__(cls)
