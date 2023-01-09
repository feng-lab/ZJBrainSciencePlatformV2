import functools
import sys
from datetime import datetime, timezone, tzinfo
from pathlib import Path
from typing import Callable, MutableSequence, Type, TypeVar

from dateutil import tz
from pydantic import BaseModel

from app.common.config import config

Model = TypeVar("Model", bound=BaseModel)
AnotherModel = TypeVar("AnotherModel", bound=BaseModel)
T = TypeVar("T")

CURRENT_TIMEZONE: tzinfo = tz.gettz(config.TIMEZONE)

SYS_PATHS = []
for sys_path in {Path(path).absolute() for path in sys.path}:
    for i, added_path in enumerate(SYS_PATHS):
        if sys_path.is_relative_to(added_path):
            SYS_PATHS.insert(i, sys_path)
            break
    else:
        SYS_PATHS.append(sys_path)


def modify_model_field_by_type(model: Model, field_type: Type[T], map_func: Callable[[T], T]):
    if model is None:
        return None
    field_schemas: dict[str, dict[str, str]] = model.schema(by_alias=False)["properties"]
    for field_name in field_schemas.keys():
        field_value = getattr(model, field_name)
        if isinstance(field_value, field_type):
            setattr(model, field_name, map_func(field_value))
        if isinstance(field_value, BaseModel):
            modify_model_field_by_type(field_value, field_type, map_func)
    return model


def protobuf_to_pydantic(model: T | None, target: type[Model]) -> Model | None:
    if model is None:
        return None
    fields = {field.name: getattr(model, field.name) for field in model.DESCRIPTOR.fields}
    for field_name, field_value in fields.items():
        if isinstance(field_value, MutableSequence):
            fields[field_name] = list(field_value)
    return target(**fields)


@functools.lru_cache(maxsize=None)
def get_module_name(module_path: Path | str) -> str | None:
    module_path = Path(module_path).absolute()
    for path in SYS_PATHS:
        if module_path.is_relative_to(path):
            return ".".join(module_path.relative_to(path).parts).rstrip(".py")
    return None


def now() -> datetime:
    return datetime.now(tz=CURRENT_TIMEZONE)


def utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)
