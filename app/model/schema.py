from datetime import date, datetime

from pydantic import BaseModel, Field

from app.db.orm import ABOBloodType, Experiment, Gender, MaritalStatus, Notification


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
    type: Notification.Type
    receiver: int = Field(ge=0)
    content: str


class NotificationCreate(NotificationBase):
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
    neuron_source: str | None = Field(max_length=50)
    stimulation_type: str | None = Field(max_length=50)
    session_num: int | None = Field(ge=0)
    trail_num: int | None = Field(ge=0)
    is_shared: bool | None


class CreateExperimentRequest(ExperimentBase):
    assistants: list[int] = Field(default_factory=list)


class ExperimentCreate(ExperimentBase):
    pass


class ExperimentInDB(ExperimentBase, BaseModelInDB):
    class Config:
        orm_mode = True


class UserInfo(BaseModel):
    id: int
    username: str
    staff_id: str

    class Config:
        orm_mode = True


class ExperimentResponse(ExperimentBase, BaseModelInDB):
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
    index: int = Field(ge=0)
    name: str = Field(max_length=255)
    extension: str = Field(max_length=50)
    size: float
    is_original: bool


class FileCreate(FileBase):
    pass


class FileInDB(FileBase, BaseModelInDB):
    class Config:
        orm_mode = True


class FileResponse(FileInDB):
    url: str | None


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
    experiment_id: int = Field(ge=0)
    brand: str = Field(max_length=255)
    name: str = Field(max_length=255)
    purpose: str = Field(max_length=255)


class CreateDeviceRequest(DeviceBase):
    pass


class DeviceWithIndex(DeviceBase):
    index: int = Field(ge=1)


class DeviceResponse(DeviceWithIndex, BaseModelInDB):
    class Config:
        orm_mode = True


class UpdateDeviceRequest(DeviceWithIndex, ModelId):
    pass


class HumanSubjectSearchable(BaseModel):
    gender: Gender | None
    abo_blood_type: ABOBloodType | None
    marital_status: MaritalStatus | None
    is_left_handed: bool | None


class HumanSubjectCreate(HumanSubjectSearchable):
    user_id: int = Field(ge=0)
    birthdate: date | None
    death_date: date | None
    education: str | None
    occupation: str | None
    phone_number: str | None
    email: str | None
    address: str | None


class HumanSubjectResponse(HumanSubjectCreate):
    pass

    class Config:
        orm_mode = True


class ExperimentIdSearch(BaseModel):
    experiment_id: int | None = Field(None, ge=0)


class HumanSubjectSearch(PageParm, HumanSubjectSearchable, ExperimentIdSearch):
    pass
