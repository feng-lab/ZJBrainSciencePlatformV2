import functools
import sys
from datetime import datetime, timezone, tzinfo
from pathlib import Path
from typing import Sequence, TypeVar

from dateutil import tz
from google.protobuf.message import Message as GrpcMessage
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


def serialize_protobuf(model):
    if model is None:
        return None
    if isinstance(model, str):
        return model
    if isinstance(model, Sequence):
        return [serialize_protobuf(item) for item in model]
    if isinstance(model, GrpcMessage):
        return {
            field.name: serialize_protobuf(getattr(model, field.name))
            for field in model.DESCRIPTOR.fields
        }
    return model


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
