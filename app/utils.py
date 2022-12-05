import functools
import importlib
import inspect
import json
from datetime import datetime
from json import JSONEncoder
from types import ModuleType
from typing import TypeVar, Callable, Any, Type

from dateutil import tz
from pydantic import BaseModel
from starlette.responses import JSONResponse

from app.config import config

Model = TypeVar("Model", bound=BaseModel)

current_timezone = tz.gettz(config.TIMEZONE)
current_timezone_offset = datetime.now(tz=current_timezone).utcoffset()


def utc_now() -> datetime:
    return datetime.now(tz=tz.UTC)


class JsonEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        return super().default(o)


class JsonResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return json.dumps(
            content, ensure_ascii=False, allow_nan=False, indent=None, separators=(",", ":"), cls=JsonEncoder
        ).encode("UTF-8")


def custom_json_response(func: Callable[..., Model]):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        response = await func(*args, **kwargs)
        json_response = JsonResponse(response.dict())
        return json_response

    return wrapper


T = TypeVar("T")


def modify_model_field_by_type(model: Model, field_type: Type[T], map_func: Callable[[T], T]):
    if model is None:
        return None

    old_dict = model.dict()
    new_dict = {
        field_name: map_func(field_value) if isinstance(field_value, field_type) else field_value
        for field_name, field_value in old_dict.items()
    }
    return model.construct(**new_dict)


def get_module_defined_members(
    module: str | ModuleType, filter_func: Callable[[str, Any], bool] | None = None
) -> list[(str, Any)]:
    if isinstance(module, str):
        module = importlib.import_module(module)
    return [
        member
        for member in inspect.getmembers(module)
        if inspect.getmodule(member[1]) == module and (filter_func is None or filter_func(member[0], member[1]))
    ]
