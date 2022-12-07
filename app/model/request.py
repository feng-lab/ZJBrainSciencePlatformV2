from datetime import datetime
from enum import Enum

from fastapi import Query
from pydantic import BaseModel, Field

from app.model.schema import File


class DeleteModelRequest(BaseModel):
    id: int


class CreateUserRequest(BaseModel):
    username: str = Field(max_length=255)
    password: str = Field(max_length=50)
    staff_id: str = Field(max_length=255)
    access_level: int = Field(ge=0)


class UpdateUserAccessLevelRequest(BaseModel):
    id: int = Field(ge=0)
    access_level: int = Field(ge=0)


class UpdatePasswordRequest(BaseModel):
    old_password: str = Field(max_length=50)
    new_password: str = Field(max_length=50)


class SendNotificationRequest(BaseModel):
    type: str = Field(title="通知类型", max_length=20)
    receiver: int = Field(title="通知接收者ID")
    content: str = Field(title="通知内容")
    create_at: datetime = Field(title="通知发送时间")


class MarkNotificationsAsReadRequest(BaseModel):
    is_all: bool = Field(description="是否标记所有通知", default=False)
    notification_ids: list[int] = Field(description="通知ID，可以有多个", default_factory=list)


class CreateExperimentRequest(BaseModel):
    name: str = Field(title="实验名称", max_length=255)
    type: str = Field(title="实验类型", max_length=50)
    location: str = Field(title="实验地点", max_length=255)
    start_at: datetime = Field(title="实验开始时间")
    end_at: datetime = Field(title="实验结束时间")
    main_operator: int = Field(title="主操作员ID")
    assistants: list[int] = Field(title="助手ID列表", default_factory=list)
    is_non_invasive: bool | None = Field(title="是否为无创实验", default=None)
    subject_type: str | None = Field(title="被试类型", default=None)
    subject_num: int | None = Field(title="被试数量", default=None)
    neuron_source: str | None = Field(title="神经元细胞来源部位", default=None)
    stimulation_type: str | None = Field(title="刺激类型", default=None)
    session_num: int | None = Field(title="实验session数量", default=None)
    trail_num: int | None = Field(title="实验trail数量", default=None)
    is_shared: bool | None = Field(title="实验数据是否公开", default=None)


class GetExperimentsByPageSortBy(Enum):
    START_TIME = "start_time"
    TYPE = "type"


class GetExperimentsByPageSortOrder(Enum):
    ASC = "asc"
    DESC = "desc"


class CreateParadigmRequest(BaseModel):
    experiment_id: int = Field(description="实验ID", ge=0)
    description: str = Field(description="范式描述")
    images: list[int] = Field(description="图片ID列表", default_factory=list)


class AddHumanSubjectRequest(BaseModel):
    class Gender(str, Enum):
        MALE = "男"
        FEMALE = "女"

    class Flag(str, Enum):
        TRUE = "是"
        FALSE = "否"

    class AboBloodType(str, Enum):
        A = "A"
        B = "B"
        AB = "AB"
        O = "O"
        OTHER = "其他"

    experiment_id: str = Field(title="实验编号")
    subject_id: str = Field(title="被试编号")
    gender: Gender = Field(title="被试性别")
    birthdate: datetime = Field(title="出生日期")
    education: str | None = Field(title="教育水平", default=None)
    occupation: str | None = Field(title="职业", default=None)
    marriage_status: Flag = Field(title="是否婚配")
    abo_blood_type: AboBloodType = Field(title="血型")
    left_hand_flag: Flag = Field(title="是否左撇子")
    death_date: datetime | None = Field(title="死亡日期", default=None)
    cellphone_number: str | None = Field(title="电话号码", default=None)
    email: str | None = Field(title="邮箱", default=None)
    address: str | None = Field(title="地址", default=None)


class UpdateHumanSubjectRequest(AddHumanSubjectRequest):
    pass


class DeleteHumanSubjectRequest(BaseModel):
    experiment_id: str = Field(title="实验编号")
    subject_id: str = Field(title="被试编号")


class AddDeviceRequest(BaseModel):
    experiment_id: str = Field(title="实验编号")
    equipment_id: str = Field(title="设备编号")
    name: str = Field(title="设备名称")
    brand: str = Field(title="设备类型")
    purpose: str | None = Field(title="实验用途", default=None)
    index: str | None = Field(title="序号", default=None)


class UpdateDeviceRequest(AddDeviceRequest):
    pass


class DeleteDeviceRequest(BaseModel):
    experiment_id: str = Field(title="实验编号")
    equipment_id: str = Field(title="设备编号")


class DisplayEEGRequest(BaseModel):
    p1: str = Field(title="文件名称")
    t: int = Field(title="时间窗口大小")
    i: int = Field(title="当前页数")
    c: str = Field(title="文件类型")


class AddTaskRequest(BaseModel):
    class TaskStep(BaseModel):
        class Type(str, Enum):
            FILTER = "filter"
            ANALYSIS = "analysis"

        type: Type = Field(title="步骤类型")

    class FilterTaskStep(TaskStep):
        class Method(str, Enum):
            IIR = "IIR"
            FIR = "FIR"

        class Window(str, Enum):
            HANMMING = "hanmming"
            HANN = "hann"
            BLACKMAN = "blackman"

        class Design(str, Enum):
            FIRWIN = "firwin"
            FIRWIN2 = "firwin2"

        l_freq: int = Field(title="L_freq")
        h_freq: int = Field(title="H_freq")
        ch_picks: int = Field(title="CH_picks")
        methods: Method = Field(title="Methods")
        params: str | None = Field(title="Params", default=None)
        length: str | None = Field(title="length", default=None)
        window: Window | None = Field(title="Window", default=None)
        design: Design | None = Field(title="Design", default=None)
        phase: str | None = Field(title="Phase", default=None)
        i_trans_bandwidth: str | None = Field(title="I_trans_bandwidth", default=None)

    class AnalysisTaskStep(TaskStep):
        analysis_list: list[str] = Field(title="analysis-list")

    task_name: str = Field(title="任务名称")
    description: str = Field(title="任务描述")
    checked_file: File = Field(title="目标文件")
    task_steps: list[FilterTaskStep | AnalysisTaskStep] = Field(title="任务名称")


class GoSearchRequest(BaseModel):
    filename: str = Field(title="待检索信号文件")
    channel: str = Field(title="通道")
    start: int = Field(title="信号起始点")
    end: int = Field(title="信号截止点")


class GetModelsByPageParam(BaseModel):
    offset: int
    limit: int
    include_deleted: bool


def get_models_by_page(
    offset: int = Query(description="分页起始位置", default=0, ge=0),
    limit: int = Query(description="分页大小", default=10, ge=0),
    include_deleted: bool = Query(description="是否包括已删除项", default=False),
) -> GetModelsByPageParam:
    return GetModelsByPageParam(offset=offset, limit=limit, include_deleted=include_deleted)
