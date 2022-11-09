import typing

from pydantic import BaseModel, Field

T = typing.TypeVar("T")


class Response(typing.Generic[T], BaseModel):
    """API响应体"""

    code: int
    """状态码，必需
    1表示成功，0和其他数字表示失败
    """

    message: str | None
    """响应消息，可选"""

    data: T | None
    """响应数据，可选"""


CODE_FAIL: int = 0
"""响应失败的code"""

CODE_SUCCESS: int = 1
"""请求成功的code"""

CODE_SESSION_TIMEOUT: int = 2
"""会话超时的失败code"""


def response_success(message: str | None = None, data: T | None = None) -> Response[T]:
    return Response(code=CODE_SUCCESS, message=message, data=data)


class GetStatisticResponse(BaseModel):
    experiments: int = Field(title="实验数量", ge=0)
    files: int = Field(title="文件数量", ge=0)
    human: int = Field(title="被试数量", ge=0)
    taskmaster: int = Field(title="任务数量", ge=0)


class GetStatisticWithDataTypeResponse(BaseModel):
    name: str = Field(title="类型名")
    value: float = Field(title="类型占比", ge=0.0, allow_inf_nan=False)
