import base64
from typing import Any, Dict, List, Tuple
import json

__all__ = ["SelectPocket"]


class SelectPocket(str):
    def get_value(self) -> Dict:
        return self.value

    def get_name(self) -> str:
        return self.value.get("name", "")

    def get_rank(self) -> int:
        return int(self.value.get("rank", -1))

    def get_score(self) -> float:
        return float(self.value.get("score", -1))

    def get_probability(self) -> float:
        return float(self.value.get("probability", -1))

    def get_center(self) -> Tuple[float]:
        return tuple(self.value.get("center")) if "center" in self.value else None

    def get_residues(self) -> List[str]:
        return self.value.get("residues") or list()

    def get_surface(self) -> List[str]:
        return self.value.get("surface") or list()

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(format="select_pocket", scope="io")

    @classmethod
    def __get_validators__(cls) -> Any:
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> "SelectPocket":
        if isinstance(value, SelectPocket):
            return value
        elif isinstance(value, str):
            p = SelectPocket(value)
            p.value = json.loads(value)
            return p
        elif isinstance(value, dict):
            p = SelectPocket(json.dumps(value))
            p.value = value
            return p
        elif isinstance(value, (bytes, bytearray, memoryview)):
            value = base64.b64encode(value).decode()
            p = SelectPocket(value)
            p.value = json.loads(value)
            return p
        else:
            raise Exception(f"SelectPocket Wrong type: {type(value)}")
