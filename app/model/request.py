from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, validator

from app.db.orm import Experiment


class DeleteModelRequest(BaseModel):
    id: int


class UpdateUserAccessLevelRequest(BaseModel):
    id: int = Field(ge=0)
    access_level: int = Field(ge=0)


class UpdatePasswordRequest(BaseModel):
    old_password: str = Field(max_length=50)
    new_password: str = Field(max_length=50)


class MarkNotificationsAsReadRequest(BaseModel):
    is_all: bool = Field(description="是否标记所有通知", default=False)
    notification_ids: list[int] = Field(description="通知ID，可以有多个", default_factory=list)


class GetExperimentsByPageSortBy(StrEnum):
    START_TIME = "start_time"
    TYPE = "type"


class GetExperimentsByPageSortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


class UpdateExperimentRequest(BaseModel):
    id: int = Field(ge=0)
    name: str | None = Field(max_length=255)
    type: Experiment.Type | None
    location: str | None = Field(max_length=255)
    start_at: datetime | None
    end_at: datetime | None
    main_operator: int | None = Field(ge=0)
    is_non_invasive: bool | None
    subject_type: str | None = Field(max_length=50)
    subject_num: int | None = Field(ge=0)
    neuron_source: str | None = Field(max_length=50)
    stimulation_type: str | None = Field(max_length=50)
    session_num: int | None = Field(ge=0)
    trail_num: int | None = Field(ge=0)
    is_shared: bool | None


class UpdateExperimentAssistantsRequest(BaseModel):
    experiment_id: int = Field(ge=0)
    assistant_ids: list[int] = Field(min_items=1)


class UpdateExperimentHumanSubjectRequest(BaseModel):
    experiment_id: int = Field(ge=0)
    user_ids: list[int] = Field(min_items=1)


class UpdateParadigmRequest(BaseModel):
    id: int = Field(ge=0)
    experiment_id: int | None = Field(ge=0)
    creator: int | None = Field(ge=0)
    description: str | None
    images: list[int] | None


class UpdateParadigmFilesRequest(BaseModel):
    paradigm_id: int = Field(ge=0)
    file_ids: list[int] = Field(min_items=1)


class DisplayEEGRequest(BaseModel):
    class FileType(StrEnum):
        EDF = "edf"
        BDF = "bdf"

    file_id: int = Field(ge=0)
    window: int = Field(ge=0)
    page_index: int = Field(ge=0)
    channels: list[str]


def validate_ids(field_name: str):
    def validate_id(value: int) -> int:
        if value < 0:
            raise ValueError("id必须是正数")
        return value

    return validator(field_name, each_item=True, allow_reuse=True)(validate_id)


class DeleteHumanSubjectRequest(BaseModel):
    user_ids: list[int]

    validate_user_ids = validate_ids("user_ids")


class DeleteDevicesRequest(BaseModel):
    device_ids: list[int]

    validate_device_ids = validate_ids("device_ids")


class UpdateDevicesInExperimentRequest(BaseModel):
    experiment_id: int = Field(ge=0)
    device_ids: list[int]

    validate_device_ids = validate_ids("device_ids")
