import functools
import json
from datetime import datetime
from json import JSONEncoder
from typing import Any, Awaitable, Callable, Generic, TypeVar

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel
from starlette.responses import JSONResponse

from app.common.util import Model

CODE_SUCCESS: int = 0
"""请求成功的code"""

CODE_FAIL: int = 1
"""响应失败的code"""

CODE_SESSION_TIMEOUT: int = 2
"""会话超时的失败code"""

MESSAGE_SUCCESS: str = "success"

Data = TypeVar("Data")


class Response(GenericModel, Generic[Data]):
    code: int = Field(title="状态码", description="1表示成功，0和其他数字表示失败", default=CODE_SUCCESS)
    message: str | None = Field(title="响应消息", default=MESSAGE_SUCCESS)
    data: Data = Field(title="响应数据")


class NoneResponse(Response[type(None)]):
    data: type(None) = None


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


def wrap_api_response(func: Callable[..., Awaitable[Data]]):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> JsonResponse:
        response_data = await func(*args, **kwargs)
        response = Response[Data](data=response_data)
        json_response = JsonResponse(response.dict())
        return json_response

    return wrapper


class LoginResponse(BaseModel):
    access_token: str
    token_type: str


class PagedData(GenericModel, Generic[Model]):
    total: int
    items: list[Model]


class AccessTokenData(BaseModel):
    # 用户ID，按照JWT标准存储为string
    sub: str
    # 过期时间，UTC
    exp: datetime
