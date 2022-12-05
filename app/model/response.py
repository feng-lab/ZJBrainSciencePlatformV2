import functools
import json
from datetime import datetime
from json import JSONEncoder
from typing import TypeVar, Generic, Any, Callable, Awaitable

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel
from starlette.responses import JSONResponse

from app.model.db_model import User, Experiment, Notification
from app.model.schema import Paradigm, Human, Device, EEGData, File, Task, SearchFile, SearchResult

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
            content, ensure_ascii=False, allow_nan=False, indent=None, separators=(",", ":"), cls=JsonEncoder
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


UserInfo = User.get_pydantic(exclude={"hashed_password"})


class ListUserData(BaseModel):
    total: int = Field(title="总数", ge=0)
    items: list[UserInfo] = Field(title="数据列表")


NotificationInfo = Notification.get_pydantic()

ExperimentInfo = Experiment.get_pydantic()


class GetExperimentInfoResponse(Response):
    data: ExperimentInfo


class GetStatisticResponse(Response):
    class Data(BaseModel):
        experiments: int = Field(title="实验数量", ge=0)
        files: int = Field(title="文件数量", ge=0)
        human: int = Field(title="被试数量", ge=0)
        taskmaster: int = Field(title="任务数量", ge=0)

    data: Data | None


class GetStatisticWithDataTypeResponse(Response):
    class Data(BaseModel):
        name: str = Field(title="类型名")
        value: float = Field(title="类型占比", ge=0.0, allow_inf_nan=False)

    data: list[Data] | None


class GetStatisticWithSubjectResponse(Response):
    class Data(BaseModel):
        type: str = Field(title="性别", description="男性或女性")
        below_30: int = Field(title="30岁以下", ge=0)
        between_30_and_60: int = Field(title="30岁到60岁之间", ge=0)
        over_60: int = Field(title="60岁以上", ge=0)

    data: list[Data] | None


class GetStatisticWithServerResponse(Response):
    data: float = Field(title="服务器资源利用率", ge=0.0, le=100.0)


class GetStatisticWithDataResponse(Response):
    data: list[list[float]] = Field(title="每天数据", description="每天数据的格式：[UTC毫秒时间戳，数值(GB)]")


class GetStatisticWithSickResponse(Response):
    class Data(BaseModel):
        sick: str = Field(title="疾病")
        part1: int = Field(title="单位1")
        part2: int = Field(title="单位2")
        part3: int = Field(title="单位3")

    data: list[Data]


class AddParadigmResponse(Response):
    pass


class GetParadigmsResponse(Response):
    data: list[Paradigm]


class GetParadigmByIdResponse(Response):
    data: Paradigm


class DeleteParadigmsResponse(Response):
    pass


class GetDocTypeResponse(Response):
    data: list[str]


class GetDocByPageResponse(Response):
    class Data(BaseModel):
        file_id: int = Field(title="文件ID")
        name: str = Field(title="文件名称")
        url: str = Field(title="文件访问地址")

    data: list[Data]


class DeleteDocResponse(Response):
    pass


class AddFileResponse(Response):
    class Data(BaseModel):
        name: str = Field(title="文件名称")
        url: str = Field(title="文件访问地址")

    data: list[Data]


class GetHumanSubjectByPageResponse(Response):
    data: list[Human]


class AddHumanSubjectResponse(Response):
    pass


class UpdateHumanSubjectResponse(Response):
    pass


class DeleteHumanSubjectResponse(Response):
    pass


class GetDeviceByPageResponse(Response):
    data: list[Device]


class AddDeviceResponse(Response):
    pass


class GetDeviceByIdResponse(Response):
    data: Device


class UpdateDeviceResponse(Response):
    pass


class DeleteDeviceResponse(Response):
    pass


class DisplayEEGResponse(Response):
    data: EEGData


class GetFilesResponse(Response):
    data: list[File]


class GetTaskByPageResponse(Response):
    data: list[Task]


class AddTaskResponse(Response):
    pass


class GetTaskByIDResponse(Response):
    data: Task


class GetTaskStepsByIDResponse(Response):
    data: list[Task.Steps]


class GetFilterStepResultByIDResponse(Response):
    data: list[list[float]]


class GetAnalysisStepResultByIDResponse(Response):
    data: str


class UploadSearchFileResponse(Response):
    data: SearchFile


class GoSearchResponse(Response):
    data: list[SearchResult]


class AccessTokenData(BaseModel):
    # 用户ID，按照JWT标准存储为string
    sub: str
    # 过期时间，UTC
    exp: datetime
