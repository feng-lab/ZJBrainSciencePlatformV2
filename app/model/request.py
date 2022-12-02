from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from app.model.schema import File


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


class LoginRequest(BaseModel):
    account: str = Field(title="用户名")
    password: str = Field(title="用户密码")


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
    is_non_invasive: bool | None = Field(title="是否为无创实验", default=None)
    subject_type: str | None = Field(title="被试类型", default=None)
    subject_num: int | None = Field(title="被试数量", default=None)
    neuron_source: str | None = Field(title="神经元细胞来源部位", default=None)
    stimulation_type: str | None = Field(title="刺激类型", default=None)
    session_num: int | None = Field(title="实验session数量", default=None)
    trail_num: int | None = Field(title="实验trail数量", default=None)
    is_shared: bool | None = Field(title="实验数据是否公开", default=None)


class GetExperimentsByPageRequest:
    class SortBy(str, Enum):
        START_TIME = ("starttime",)
        TYPE = ("type",)

    class SortOrder(str, Enum):
        ASC = ("asce",)
        DESC = "desc"


class AddParadigmRequest(BaseModel):
    img_url: list[str] = Field(title="图片地址", default_factory=list)
    desc: str = Field(title="文字描述")
    experiment_id: str = Field(title="实验编号")
    creator: str = Field(title="创建者用户名")
    create_time: datetime = Field(title="创建时间")


class DeleteParadigmsRequest(BaseModel):
    experiment_id: str = Field(title="实验编号")
    paradigm_id: str = Field(alias="id", title="实验范式id")


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


class MarkMsgRequest(BaseModel):
    account: str = Field(title="登录用户账号名")
    ids: str = Field(title="消息id,多个id则逗号分隔")
