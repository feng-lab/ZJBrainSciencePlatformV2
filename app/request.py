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
