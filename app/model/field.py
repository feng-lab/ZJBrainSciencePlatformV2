import json
from json import JSONDecodeError
from typing import Callable, TypeVar

Varchar = TypeVar("Varchar", bound=str)
VarcharValidator = Callable[[str], Varchar]


class ID(int):
    @classmethod
    def __get_validators__(cls):
        yield cls._validate

    @staticmethod
    def _validate(value):
        value = int(value)
        if value < 0:
            raise ValueError("negative ID")
        return ID(value)


class LongVarchar(str):
    @classmethod
    def __get_validators__(cls):
        yield _get_varchar_validator(cls, 255)


class ShortVarchar(str):
    @classmethod
    def __get_validators__(cls):
        yield _get_varchar_validator(cls, 50)


Text = str


class JsonText(str):
    @classmethod
    def __get_validators__(cls):
        yield cls._validate

    @staticmethod
    def _validate(value):
        if not isinstance(value, str):
            raise TypeError("not str")
        try:
            _ = json.loads(value)
        except JSONDecodeError as e:
            raise ValueError("invalid json") from e
        else:
            return JsonText(value)


class JsonDict(dict):
    @classmethod
    def __get_validators__(cls):
        yield cls._validate

    @staticmethod
    def _validate(value):
        if not isinstance(value, dict):
            raise TypeError("not dict")
        if not JsonDict._is_valid_dict(value):
            raise ValueError("invalid json dict")
        return JsonDict(value)

    @staticmethod
    def _is_valid_value(v) -> bool:
        return (
            v is None
            or isinstance(v, int)
            or isinstance(v, float)
            or isinstance(v, bool)
            or isinstance(v, str)
            or (isinstance(v, list) and JsonDict._is_valid_list(v))
            or (isinstance(v, dict) and JsonDict._is_valid_dict(v))
        )

    @staticmethod
    def _is_valid_list(l: list) -> bool:
        return all(JsonDict._is_valid_value(item) for item in l)

    @staticmethod
    def _is_valid_dict(d: dict) -> bool:
        return all(
            isinstance(key, str) and JsonDict._is_valid_value(value) for key, value in d.items()
        )


def _get_varchar_validator(cls: type[Varchar], max_length: int) -> VarcharValidator:
    def validate(value: str):
        if not isinstance(value, str):
            raise TypeError("not str")
        if len(value) > max_length:
            raise ValueError(f"too long string, {len(value)}>{max_length}")
        return cls(value)

    return validate
