from fastapi import APIRouter, Depends

import app.external.model as algo_rpc
from app.api.file import get_os_path
from app.common.context import ResearcherContext
from app.common.exception import ServiceError
from app.db import common_crud
from app.db.orm import File
from app.external import rpc
from app.model.request import DisplayEEGRequest
from app.model.response import Response, wrap_api_response

router = APIRouter(tags=["algorithm"])


@router.post(
    "/api/displayEEG", description="查看EEG数据", response_model=Response[algo_rpc.DisplayEEGResponse]
)
@wrap_api_response
def display_eeg(
    request: DisplayEEGRequest, ctx: ResearcherContext = Depends()
) -> algo_rpc.DisplayEEGResponse:
    file = common_crud.get_row_by_id(ctx.db, File, request.file_id)
    if file is None:
        raise ServiceError.not_found("文件不存在")
    file_path = str(get_os_path(file.experiment_id, file.id, file.extension))
    rpc_request = algo_rpc.DisplayEEGRequest(
        file_info=algo_rpc.FileInfo(id=file.id, path=file_path, type=file.extension),
        window=request.window,
        page_index=request.page_index,
        channels=request.channels,
    )
    return rpc.display_eeg(rpc_request)
