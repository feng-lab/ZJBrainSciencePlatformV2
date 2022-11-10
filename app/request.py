from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    account: str = Field(title="用户名")
    password: str = Field(title="用户密码")


class AddExperimentRequest(BaseModel):
    experiment_title: str = Field(title="实验名称")
    experiment_type: str = Field(title="实验类型")
    non_invasive_flag: bool = Field(title="是否无创")
    location: str = Field(title="实验地点")
    start_date: datetime = Field(title="实验开始日期")
    end_date: datetime = Field(title="实验结束日期")
    subject_type: str = Field(title="被试类型")
    number_of_subjects: int = Field(title="被试数量", ge=0)
    shared: bool = Field(title="是否公开")


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
