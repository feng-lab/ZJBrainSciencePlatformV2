import functools
import json
from datetime import date, datetime
from json import JSONEncoder
from typing import Any, Callable, Generic, TypeVar

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel
from starlette.responses import JSONResponse

from app.common.log import request_id_ctxvar
from app.common.util import AnotherModel, Model

# 请求成功的code
CODE_SUCCESS: int = 0
# 响应失败的code
CODE_FAIL: int = 1
# 会话超时的失败code
CODE_SESSION_TIMEOUT: int = 2
# 数据库操作失败
CODE_DATABASE_FAIL: int = 3
# 要获取的对象不存在
CODE_NOT_FOUND: int = 4

MESSAGE_SUCCESS: str = "success"

Data = TypeVar("Data")


class Response(GenericModel, Generic[Data]):
    code: int = Field(title="状态码", description="1表示成功，0和其他数字表示失败", default=CODE_SUCCESS)
    message: str | None = Field(title="响应消息", default=MESSAGE_SUCCESS)
    data: Data = Field(title="响应数据")
    request_id: str = Field(title="请求ID", default_factory=request_id_ctxvar.get)


NoneResponse = Response[type(None)]


class JsonEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(o, date):
            return o.strftime("%Y-%m-%d")
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


def wrap_api_response(func: Callable[..., Data]):
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> JsonResponse:
        response_data = func(*args, **kwargs)
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

    def map_items(
        self,
        target_model: type[AnotherModel] | None = None,
        func: Callable[[Model], AnotherModel] | None = None,
    ) -> None:
        def default_map_func(item: Model) -> AnotherModel:
            return target_model(**item.dict())

        if func is None:
            func = default_map_func
        for i, item in enumerate(self.items):
            self.items[i] = func(item)


class AccessTokenData(BaseModel):
    # 用户ID，按照JWT标准存储为string
    sub: str
    # 过期时间，UTC
    exp: datetime


class DisplayEEGData(BaseModel):
    class Dataset(BaseModel):
        name: str
        data: list[float]
        unit: str
        type: str
        x_label: bool
        value_decimals: int

    x_data: list[float]
    stimulation: list[int]
    datasets: list[Dataset]

    class Config:
        orm_mode = True


class CreateHumanSubjectResponse(BaseModel):
    username: str
    staff_id: str
    password: str
