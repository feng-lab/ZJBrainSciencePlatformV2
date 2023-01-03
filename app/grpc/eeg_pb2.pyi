from typing import ClassVar as _ClassVar
from typing import Iterable as _Iterable
from typing import Mapping as _Mapping
from typing import Optional as _Optional
from typing import Union as _Union

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf.internal import containers as _containers

DESCRIPTOR: _descriptor.FileDescriptor

class DisplayEEGDataset(_message.Message):
    __slots__ = ["data", "name", "type", "unit", "value_decimals", "x_label"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    VALUE_DECIMALS_FIELD_NUMBER: _ClassVar[int]
    X_LABEL_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedScalarFieldContainer[float]
    name: str
    type: str
    unit: str
    value_decimals: int
    x_label: bool
    def __init__(
        self,
        name: _Optional[str] = ...,
        data: _Optional[_Iterable[float]] = ...,
        unit: _Optional[str] = ...,
        type: _Optional[str] = ...,
        x_label: bool = ...,
        value_decimals: _Optional[int] = ...,
    ) -> None: ...

class DisplayEEGRequest(_message.Message):
    __slots__ = ["channels", "file_id", "file_path", "file_type", "page_index", "window"]
    CHANNELS_FIELD_NUMBER: _ClassVar[int]
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    FILE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PAGE_INDEX_FIELD_NUMBER: _ClassVar[int]
    WINDOW_FIELD_NUMBER: _ClassVar[int]
    channels: _containers.RepeatedScalarFieldContainer[str]
    file_id: int
    file_path: str
    file_type: str
    page_index: int
    window: int
    def __init__(
        self,
        file_id: _Optional[int] = ...,
        window: _Optional[int] = ...,
        page_index: _Optional[int] = ...,
        channels: _Optional[_Iterable[str]] = ...,
        file_path: _Optional[str] = ...,
        file_type: _Optional[str] = ...,
    ) -> None: ...

class DisplayEEGResponse(_message.Message):
    __slots__ = ["datasets", "stimulation", "x_data"]
    DATASETS_FIELD_NUMBER: _ClassVar[int]
    STIMULATION_FIELD_NUMBER: _ClassVar[int]
    X_DATA_FIELD_NUMBER: _ClassVar[int]
    datasets: _containers.RepeatedCompositeFieldContainer[DisplayEEGDataset]
    stimulation: _containers.RepeatedScalarFieldContainer[int]
    x_data: _containers.RepeatedScalarFieldContainer[float]
    def __init__(
        self,
        x_data: _Optional[_Iterable[float]] = ...,
        stimulation: _Optional[_Iterable[int]] = ...,
        datasets: _Optional[_Iterable[_Union[DisplayEEGDataset, _Mapping]]] = ...,
    ) -> None: ...
