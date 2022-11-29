import functools
import json
from datetime import timezone, datetime
from json import JSONEncoder
from typing import TypeVar, Callable, Any

from dateutil import tz
from pydantic import BaseModel
from starlette.responses import JSONResponse

from app.config import config

Model = TypeVar("Model", bound=BaseModel)

current_timezone = tz.gettz(config.TIMEZONE)
current_timezone_offset = datetime.now(tz=current_timezone).utcoffset()


def utc_now() -> datetime:
    return datetime.now(tz=tz.UTC)


# 将数据库中取出的无时区datetime对象转换为CST时区对象
def db_model_add_timezone(func: Callable[..., Model | list[Model]]):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Model | list[Model] | None:
        result = await func(*args, **kwargs)
        if result is None:
            return None
        if isinstance(result, BaseModel):
            return add_timezone(result, utc_to_current_timezone)
        if isinstance(result, list):
            return [
                add_timezone(model, utc_to_current_timezone)
                if isinstance(model, BaseModel)
                else model
                for model in result
            ]
        return result

    return wrapper


def request_add_timezone(model: Model | None) -> Model | None:
    if model is None:
        return None
    return add_timezone(model, add_current_timezone)


def add_timezone(model: Model, adder: Callable[[datetime], datetime]) -> Model:
    new_dict = {
        name: adder(value)
        if isinstance(value, datetime) and value.utcoffset() != current_timezone_offset
        else value
        for name, value in model.dict().items()

    }
    return model.construct(**new_dict)


def utc_to_current_timezone(time: datetime) -> datetime:
    return time.replace(tzinfo=timezone.utc).astimezone(current_timezone)


def add_current_timezone(time: datetime) -> datetime:
    return time.replace(tzinfo=current_timezone)


class JsonEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        return super().default(o)


class JsonResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=JsonEncoder,
        ).encode("UTF-8")


def custom_json_response(func: Callable[..., Model]):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        response = await func(*args, **kwargs)
        json_response = JsonResponse(response.dict())
        return json_response

    return wrapper
