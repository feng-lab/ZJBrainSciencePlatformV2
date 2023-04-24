from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import app.db.crud.file as file_crud
import app.external.model as rpc_model
from app.common.context import ResearcherContext
from app.common.exception import ServiceError
from app.external import rpc
from app.model.field import ID
from app.model.request import DisplayEEGRequest, DisplayNeuralSpikeRequest
from app.model.response import Response, wrap_api_response

router = APIRouter(tags=["algorithm"])


@router.post(
    "/api/displayEEG", description="查看EEG数据", response_model=Response[rpc_model.DisplayDataResponse]
)
@wrap_api_response
def display_eeg(
    request: DisplayEEGRequest, ctx: ResearcherContext = Depends()
) -> rpc_model.DisplayDataResponse:
    file_info = get_file_info(ctx.db, request.file_id)
    rpc_request = rpc_model.DisplayEEGRequest(
        file_info=file_info, **request.dict(exclude={"file_id"})
    )
    return rpc.display_eeg(rpc_request)


@router.post(
    "/api/displayNeuralSpike",
    description="查看NeuralSpike数据",
    response_model=Response[rpc_model.DisplayDataResponse],
)
@wrap_api_response
def neural_neural_spike(
    request: DisplayNeuralSpikeRequest, ctx: ResearcherContext = Depends()
) -> rpc_model.DisplayDataResponse:
    file_info = get_file_info(ctx.db, request.file_id)
    rpc_request = rpc_model.DisplayNeuralSpikeRequest(
        file_info=file_info, **request.dict(exclude={"file_id"})
    )
    return rpc.display_neural_spike(rpc_request)


@router.get(
    "/api/getEEGChannels", description="获取EEG文件的channel列表", response_model=Response[list[str]]
)
@wrap_api_response
def get_eeg_channels(file_id: ID, ctx: ResearcherContext = Depends()) -> list[str]:
    file_info = get_file_info(ctx.db, file_id)
    rpc_request = rpc_model.GetFileInfoRequest(file_info=file_info)
    rpc_response = rpc.get_eeg_channels(rpc_request)
    return rpc_response.channels


@router.get(
    "/api/getNeuralSpikeInfo",
    description="获取NeuralSpike文件信息",
    response_model=Response[rpc_model.NeuralSpikeFileInfo],
)
@wrap_api_response
def get_neural_spike_info(
    file_id: ID, ctx: ResearcherContext = Depends()
) -> rpc_model.NeuralSpikeFileInfo:
    file_info = get_file_info(ctx.db, file_id)
    rpc_request = rpc_model.GetFileInfoRequest(file_info=file_info)
    return rpc.get_neural_spike_info(rpc_request)


def get_file_info(db: Session, file_id: ID) -> rpc_model.FileInfo:
    file_info = file_crud.get_algorithm_file_info(db, file_id)
    if file_info is None:
        raise ServiceError.not_found("文件不存在")
    return file_info
