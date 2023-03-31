from fastapi import APIRouter, Depends

import app.external.model as rpc_model
from app.api.file import get_os_path
from app.common.context import ResearcherContext
from app.common.exception import ServiceError
from app.db import common_crud
from app.db.orm import File
from app.external import rpc
from app.model.field import ID
from app.model.request import DisplayEEGRequest
from app.model.response import Response, wrap_api_response

router = APIRouter(tags=["algorithm"])


@router.post(
    "/api/displayEEG", description="查看EEG数据", response_model=Response[rpc_model.DisplayEEGResponse]
)
@wrap_api_response
def display_eeg(
    request: DisplayEEGRequest, ctx: ResearcherContext = Depends()
) -> rpc_model.DisplayEEGResponse:
    file = common_crud.get_row_by_id(ctx.db, File, request.file_id)
    if file is None:
        raise ServiceError.not_found("文件不存在")
    file_path = str(get_os_path(file.experiment_id, file.id, file.extension))
    rpc_request = rpc_model.DisplayEEGRequest(
        file_info=rpc_model.FileInfo(id=file.id, path=file_path, type=file.extension),
        window=request.window,
        page_index=request.page_index,
        channels=request.channels,
    )
    return rpc.display_eeg(rpc_request)


@router.get(
    "/api/getEEGChannels", description="获取EEG文件的channel列表", response_model=Response[list[str]]
)
@wrap_api_response
def get_eeg_channels(file_id: ID, ctx: ResearcherContext = Depends()) -> list[str]:
    file = common_crud.get_row_by_id(ctx.db, File, file_id)
    if file is None:
        raise ServiceError.not_found("文件不存在")
    file_path = str(get_os_path(file.experiment_id, file.id, file.extension))
    rpc_request = rpc_model.GetEEGChannelsRequest(
        file_info=rpc_model.FileInfo(id=file.id, path=file_path, type=file.extension)
    )
    rpc_response = rpc.get_eeg_channels(rpc_request)
    return rpc_response.channels
