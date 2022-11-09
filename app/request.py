from datetime import datetime

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
