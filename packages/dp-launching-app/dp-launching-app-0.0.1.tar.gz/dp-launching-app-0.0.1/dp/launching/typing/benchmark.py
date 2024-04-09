from typing import Any, Dict, List

__all__ = ["BenchmarkTags"]


class BenchmarkTags(list):
    def get_value(self) -> List:
        if hasattr(self, "value"):
            return self.value
        return []

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(format="benchmark_tags", scope="executor")

    @classmethod
    def __get_validators__(cls) -> Any:  # type: ignore
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> "BenchmarkTags":
        if isinstance(value, list):
            f = BenchmarkTags(value)
            f.value = value
            return f
        else:
            raise Exception(f"BenchmarkTags Wrong type: {type(value)}")
