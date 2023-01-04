from datetime import datetime

from pydantic import BaseModel, Field

from app.common import time
from app.db.orm import Experiment, Notification


class BaseModelCreate(BaseModel):
    gmt_create: datetime
    gmt_modified: datetime
    is_deleted: bool = False

    def __init__(self, **kwargs):
        # 保证gmt_create与gmt_modified的默认值相同
        now = time.now()
        kwargs = kwargs | {"gmt_create": now, "gmt_modified": now}
        super().__init__(**kwargs)


class ModelId(BaseModel):
    id: int = Field(ge=0)


class BaseModelInDB(BaseModelCreate, ModelId):
    pass


class UserBase(BaseModel):
    username: str = Field(max_length=255)
    staff_id: str = Field(max_length=50)
    access_level: int = Field(ge=0)


class CreateUserRequest(UserBase):
    password: str = Field(max_length=255)


class UserPassword(BaseModel):
    hashed_password: str = Field(max_length=255)


class UserAuth(UserBase, ModelId, UserPassword):
    class Config:
        orm_mode = True


class UserCreate(UserBase, UserPassword, BaseModelCreate):
    pass


class UserSessionMixin(BaseModel):
    last_login_time: datetime | None
    last_logout_time: datetime | None


class UserInDB(UserCreate, UserSessionMixin, BaseModelInDB):
    class Config:
        orm_mode = True


class UserResponse(UserBase, UserSessionMixin, BaseModelInDB):
    pass


class NotificationBase(BaseModel):
    type: Notification.Type
    receiver: int = Field(ge=0)
    content: str


class NotificationCreate(NotificationBase, BaseModelCreate):
    creator: int = Field(ge=0)
    status: Notification.Status


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
    type: Experiment.Type
    location: str = Field(max_length=255)
    start_at: datetime
    end_at: datetime
    main_operator: int = Field(ge=0)
    is_non_invasive: bool | None
    subject_type: str | None = Field(max_length=50)
    subject_num: int | None = Field(ge=0)
    neuron_source: str | None = Field(50)
    stimulation_type: str | None = Field(50)
    session_num: int | None = Field(ge=0)
    trail_num: int | None = Field(ge=0)
    is_shared: bool | None


class CreateExperimentRequest(ExperimentBase):
    assistants: list[int] = Field(default_factory=list)


class ExperimentCreate(ExperimentBase, BaseModelCreate):
    pass


class ExperimentInDB(ExperimentBase, BaseModelInDB):
    class Config:
        orm_mode = True


class ExperimentResponse(CreateExperimentRequest, BaseModelInDB):
    pass


class ExperimentAssistantBase(BaseModel):
    user_id: int = Field(ge=0)
    experiment_id: int = Field(ge=0)


class ExperimentAssistantCreate(ExperimentAssistantBase, BaseModelCreate):
    pass


class ExperimentAssistantInDB(ExperimentAssistantBase, BaseModelInDB):
    pass


class FileBase(BaseModel):
    experiment_id: int = Field(ge=0)
    index: int = Field(ge=0)
    path: str = Field(max_length=255)
    extension: str = Field(max_length=50)
    size: float
    is_original: bool


class FileCreate(FileBase, BaseModelCreate):
    pass


class FileInDB(FileBase, BaseModelInDB):
    class Config:
        orm_mode = True


class FileResponse(FileInDB):
    pass


class ParadigmBase(BaseModel):
    experiment_id: int = Field(ge=0)
    description: str


class CreateParadigmRequest(ParadigmBase):
    images: list[int]


class ParadigmCreate(ParadigmBase, BaseModelCreate):
    creator: int = Field(ge=0)


class ParadigmInDB(ParadigmBase, BaseModelInDB):
    class Config:
        orm_mode = True


class ParadigmResponse(CreateParadigmRequest, BaseModelInDB):
    pass


class ParadigmFileBase(BaseModel):
    paradigm_id: int = Field(ge=0)
    file_id: int = Field(ge=0)
