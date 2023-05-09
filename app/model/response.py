from datetime import datetime
from enum import IntEnum
from typing import Generic, TypeAlias, TypeVar

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

from app.common.log import request_id_ctxvar
from app.common.util import Model

Data = TypeVar("Data")


class ResponseCode(IntEnum):
    SUCCESS = 0
    SERVER_ERROR = 1
    PARAMS_ERROR = 2
    UNAUTHORIZED = 3
    SESSION_TIMEOUT = 4


class Response(GenericModel, Generic[Data]):
    code: int = Field(ResponseCode.SUCCESS, title="状态码", description="1表示成功，0和其他数字表示失败")
    message: str | None = Field(None, title="响应消息")
    data: Data = Field(title="响应数据")
    request_id: str = Field(title="请求ID", default_factory=request_id_ctxvar.get)


NoneResponse: TypeAlias = Response[type(None)]


class LoginResponse(BaseModel):
    access_token: str
    token_type: str


class Page(GenericModel, Generic[Model]):
    total: int
    items: list[Model]


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
    user_id: int
    username: str
    staff_id: str
    password: str
