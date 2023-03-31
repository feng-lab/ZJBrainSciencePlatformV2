from enum import IntEnum, StrEnum
from typing import Generic, TypeVar

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

from app.model.field import ID

Data = TypeVar("Data")


class ResponseCode(IntEnum):
    SUCCESS = 0
    FAIL = 1


class Response(GenericModel, Generic[Data]):
    code: ResponseCode
    message: str
    request_id: str | None
    data: Data


class FileType(StrEnum):
    EDF = "edf"
    BDF = "bdf"
    FIF = "fif"


class FileInfo(BaseModel):
    id: ID | None
    path: str
    type: FileType


class DisplayEEGRequest(BaseModel):
    file_info: FileInfo
    window: int = Field(ge=0)
    page_index: int = Field(ge=0)
    channels: list[str]


class DisplayEEGResponse(BaseModel):
    class Dataset(BaseModel):
        name: str
        data: list[float]
        unit: str
        type: str
        x_label: bool
        value_decimals: int

    x_data: list[float]
    stimulation: list[int]
    datasets: list[Dataset]


class GetEEGChannelsRequest(BaseModel):
    file_info: FileInfo


class GetEEGChannelsResponse(BaseModel):
    channels: list[str]
