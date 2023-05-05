from datetime import date, datetime

from pydantic import BaseModel, Field, validator

from app.model.enum_filed import (
    ABOBloodType,
    ExperimentType,
    Gender,
    GetExperimentsByPageSortBy,
    GetExperimentsByPageSortOrder,
    MaritalStatus,
    NotificationStatus,
    NotificationType,
    TaskStatus,
    TaskStepType,
    TaskType,
)
from app.model.field import ID, JsonDict, LongVarchar, ShortVarchar, Text


class ModelId(BaseModel):
    id: int = Field(ge=0)


class BaseModelInDB(ModelId):
    gmt_create: datetime
    gmt_modified: datetime
    is_deleted: bool


class PageParm(BaseModel):
    offset: int = Field(0, ge=0)
    limit: int = Field(10, ge=0)
    include_deleted: bool = Field(False)


class ExperimentIdSearch(BaseModel):
    experiment_id: int | None = Field(None, ge=0)


class UserNameStaffId(BaseModel):
    username: str = Field(max_length=255)
    staff_id: str = Field(max_length=50)


class UserBase(UserNameStaffId):
    access_level: int = Field(ge=0)


class CreateUserRequest(UserBase):
    password: str = Field(max_length=255)


class UserPassword(BaseModel):
    hashed_password: str = Field(max_length=255)


class UserAuth(UserBase, ModelId, UserPassword):
    class Config:
        orm_mode = True


class UserCreate(UserBase, UserPassword):
    pass


class UserSessionMixin(BaseModel):
    last_login_time: datetime | None
    last_logout_time: datetime | None


class UserInDB(UserCreate, UserSessionMixin, BaseModelInDB):
    class Config:
        orm_mode = True


class UserResponse(UserBase, UserSessionMixin, BaseModelInDB):
    class Config:
        orm_mode = True


class NotificationBase(BaseModel):
    type: NotificationType
    receiver: int = Field(ge=0)
    content: str


class NotificationCreate(NotificationBase):
    creator: int = Field(ge=0)
    status: NotificationStatus


class NotificationInDB(NotificationCreate, BaseModelInDB):
    class Config:
        orm_mode = True


class NotificationResponse(NotificationInDB):
    creator_name: str


class TaskStepStatusNotification(BaseModel):
    task_id: int
    task_name: str
    task_status: int


class ExperimentBase(BaseModel):
    name: str = Field(max_length=255)
    description: str
    type: ExperimentType
    location: str = Field(max_length=255)
    start_at: datetime
    end_at: datetime
    main_operator: int = Field(ge=0)
    is_non_invasive: bool | None
    subject_type: str | None = Field(max_length=50)
    subject_num: int | None = Field(ge=0)
    neuron_source: str | None = Field(max_length=50)
    stimulation_type: str | None = Field(max_length=50)
    session_num: int | None = Field(ge=0)
    trail_num: int | None = Field(ge=0)
    is_shared: bool | None


class CreateExperimentRequest(ExperimentBase):
    assistants: list[int] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class ExperimentInDB(ExperimentBase, BaseModelInDB):
    class Config:
        orm_mode = True


class UserInfo(BaseModel):
    id: int
    username: str
    staff_id: str

    class Config:
        orm_mode = True


class ExperimentSearch(PageParm):
    name: str | None
    type: str | None
    tag: str | None
    sort_by: GetExperimentsByPageSortBy = GetExperimentsByPageSortBy.START_TIME
    sort_order: GetExperimentsByPageSortOrder = GetExperimentsByPageSortOrder.DESC


class ExperimentSimpleResponse(ExperimentBase, ModelId):
    tags: list[str]


class ExperimentResponse(ExperimentSimpleResponse):
    main_operator: UserInfo
    assistants: list[UserInfo]


class ExperimentAssistantBase(BaseModel):
    user_id: int = Field(ge=0)
    experiment_id: int = Field(ge=0)


class ExperimentAssistantCreate(ExperimentAssistantBase):
    pass


class ExperimentAssistantInDB(ExperimentAssistantBase, BaseModelInDB):
    pass


class FileBase(BaseModel):
    experiment_id: int = Field(ge=0)
    paradigm_id: int | None = Field(ge=0)
    name: str = Field(max_length=255)
    file_type: str = Field(max_length=50)
    size: float
    is_original: bool


class FileCreate(FileBase):
    pass


class FileSearch(PageParm, ExperimentIdSearch):
    name: str = Field("", max_length=255)
    file_type: str = Field("", max_length=255)


class FileResponse(FileBase, ModelId):
    url: str | None

    class Config:
        orm_mode = True


class ParadigmBase(BaseModel):
    experiment_id: int = Field(ge=0)
    description: str


class CreateParadigmRequest(ParadigmBase):
    images: list[int]


class ParadigmCreate(ParadigmBase):
    creator: int = Field(ge=0)


class ParadigmInDB(ParadigmCreate, BaseModelInDB):
    class Config:
        orm_mode = True


class ParadigmResponse(CreateParadigmRequest, BaseModelInDB):
    creator: UserInfo


class ParadigmFileBase(BaseModel):
    paradigm_id: int = Field(ge=0)
    file_id: int = Field(ge=0)


class ParadigmFileCreate(ParadigmFileBase):
    pass


class DeviceBase(BaseModel):
    brand: str = Field(max_length=255)
    name: str = Field(max_length=255)
    purpose: str = Field(max_length=255)


class CreateDeviceRequest(DeviceBase):
    pass


class DeviceInfo(DeviceBase, ModelId):
    class Config:
        orm_mode = True


class DeviceInfoWithIndex(DeviceInfo):
    index: int | None = Field(ge=1)


class DeviceSearch(PageParm, ExperimentIdSearch):
    brand: str | None
    name: str | None


class UpdateDeviceRequest(DeviceBase, ModelId):
    pass


class HumanSubjectSearchable(BaseModel):
    name: ShortVarchar | None
    gender: Gender | None
    abo_blood_type: ABOBloodType | None
    marital_status: MaritalStatus | None
    is_left_handed: bool | None


class HumanSubjectCreate(HumanSubjectSearchable):
    birthdate: date | None
    death_date: date | None
    education: str | None
    occupation: str | None
    phone_number: str | None
    email: str | None
    address: str | None

    @validator("death_date", pre=True)
    def parse_date(cls, value):
        if isinstance(value, str) and len(value) < 1:
            return None
        return value


class HumanSubjectUpdate(HumanSubjectCreate):
    user_id: int = Field(ge=0)


class HumanSubjectResponse(HumanSubjectUpdate, UserNameStaffId):
    pass


class HumanSubjectSearch(PageParm, HumanSubjectSearchable, ExperimentIdSearch):
    pass


class TaskSourceFileSearch(PageParm):
    name: str | None = Field(None, max_length=255)
    file_type: str | None = Field(None, max_length=50)
    experiment_name: str | None = Field(None, max_length=255)


class TaskSourceFileResponse(ModelId):
    name: str = Field(max_length=255)
    file_type: str = Field(max_length=50)
    experiment_id: int = Field(ge=0)
    experiment_name: str = Field(max_length=255)


class TaskBase(BaseModel):
    name: LongVarchar
    description: Text
    source_file: ID


class TaskStepCreate(BaseModel):
    name: LongVarchar
    step_type: TaskStepType
    parameters: JsonDict


class TaskStepBase(TaskStepCreate):
    task_id: ID


class TaskCreate(TaskBase):
    steps: list[TaskStepCreate] = Field(default_factory=list)


class TaskStepInfo(TaskStepBase):
    index: int = Field(ge=1)
    status: TaskStatus
    start_at: datetime | None
    end_at: datetime | None


class TaskBaseInfo(TaskBase):
    type: TaskType
    status: TaskStatus
    start_at: datetime | None
    end_at: datetime | None
    creator: UserInfo


class TaskInfo(TaskBaseInfo):
    steps: list[TaskStepInfo]


class TaskSearch(PageParm):
    name: LongVarchar | None
    type: TaskType | None
    source_file: int | None
    status: TaskStatus | None
    start_at: date | None
    creator: int | None
