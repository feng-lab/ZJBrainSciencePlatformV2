from typing import Any, Optional

from .models import *


class Response(BaseModel):
    code: int = Field(title="状态码", description="1表示成功，0和其他数字表示失败")
    message: str | None = Field(title="响应消息", default=None)
    data: Any | None = Field(title="响应数据", default=None)


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


class GetStatisticWithSickResponse(Response):
    class Data(BaseModel):
        sick: str = Field(title="疾病")
        part1: int = Field(title="单位1")
        part2: int = Field(title="单位2")
        part3: int = Field(title="单位3")

    data: list[Data]


class AddExperimentResponse(Response):
    pass


# TODO 添加必要字段
class GetExperimentsByPageResponse(Response):
    data: list[Experiment]


class GetExperimentsByIdResponse(Response):
    data: Experiment


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
