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
    data: Data


NoneResponse = Response[type(None)]


class FileType(StrEnum):
    EDF = "edf"
    BDF = "bdf"
    FIF = "fif"
    NEV = "nev"

    @staticmethod
    def is_valid_file_type(file_type: str) -> bool:
        for ft in FileType:
            if file_type == ft:
                return True
        return False


class FileInfo(BaseModel):
    id: ID | None
    path: str
    type: FileType


class BaseDisplayDataRequest(BaseModel):
    file_info: FileInfo
    window: int = Field(ge=0)
    page_index: int = Field(ge=0)


class DisplayEEGRequest(BaseDisplayDataRequest):
    channels: list[str]


class DisplayNeuralSpikeRequest(BaseDisplayDataRequest):
    block_index: int = Field(0, ge=0)
    segment_index: int = Field(0, ge=0)
    analog_signal_index: int = Field(0, ge=0)
    channel_indexes: list[int] | None = None


class DisplayDataResponse(BaseModel):
    class Dataset(BaseModel):
        name: str
        data: list[float]
        unit: str
        value_decimals: int

    x_data: list[float]
    stimulation: list[int]
    datasets: list[Dataset]


class GetFileInfoRequest(BaseModel):
    file_info: FileInfo


class GetEEGChannelsRequest(BaseModel):
    file_info: FileInfo


class GetEEGChannelsResponse(BaseModel):
    channels: list[str]


class AnalogSignalInfo(BaseModel):
    analog_signal_index: int
    start_time: int
    end_time: int
    sampling_rate: float
    channel_count: int


class SegmentInfo(BaseModel):
    segment_index: int
    analog_signals: list[AnalogSignalInfo]


class BlockInfo(BaseModel):
    block_index: int
    segments: list[SegmentInfo]


class NeuralSpikeFileInfo(BaseModel):
    blocks: list[BlockInfo]
