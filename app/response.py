from typing import Any, Optional

from pydantic import BaseModel, Field


class Response(BaseModel):
    """API响应体"""

    code: int
    """状态码，必需
    1表示成功，0和其他数字表示失败
    """

    message: Optional[str]
    """响应消息，可选"""

    data: Optional[Any]
    """响应数据，可选"""


CODE_FAIL: int = 0
"""响应失败的code"""

CODE_SUCCESS: int = 1
"""请求成功的code"""

CODE_SESSION_TIMEOUT: int = 2
"""会话超时的失败code"""


class LoginResponse(Response):
    pass


class GetStatisticResponse(Response):
    class Data(BaseModel):
        experiments: int = Field(title="实验数量", ge=0)
        files: int = Field(title="文件数量", ge=0)
        human: int = Field(title="被试数量", ge=0)
        taskmaster: int = Field(title="任务数量", ge=0)

    data: Optional[Data]


class GetStatisticWithDataTypeResponse(Response):
    class Data(BaseModel):
        name: str = Field(title="类型名")
        value: float = Field(title="类型占比", ge=0.0, allow_inf_nan=False)

    data: Optional[list[Data]]


class GetStatisticWithSubjectResponse(Response):
    class Data(BaseModel):
        type: str = Field(title="性别", description="男性或女性")
        below_30: int = Field(title="30岁以下", ge=0)
        between_30_and_60: int = Field(title="30岁到60岁之间", ge=0)
        over_60: int = Field(title="60岁以上", ge=0)

    data: Optional[list[Data]]


class GetStatisticWithServerResponse(Response):
    data: float = Field(title="服务器资源利用率", ge=0.0, le=100.0)


class GetStatisticWithDataResponse(Response):
    data: list[list[float]] = Field(
        title="每天数据", description="每天数据的格式：[UTC毫秒时间戳，数值(GB)]"
    )
