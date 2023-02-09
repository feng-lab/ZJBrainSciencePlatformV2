from typing import Any

from fastapi import APIRouter, Depends

from app.api.file import get_os_path
from app.common.context import Context, researcher_context
from app.common.depend import grpc_stub
from app.common.util import serialize_protobuf
from app.db import common_crud
from app.db.orm import File
from app.grpc.eeg_pb2 import DisplayEEGRequest as GrpcDisplayEEGRequest
from app.grpc.eeg_pb2_grpc import EEGServiceStub
from app.model.request import DisplayEEGRequest
from app.model.response import Response, wrap_api_response

router = APIRouter(tags=["algorithm"])


@router.post("/api/displayEEG", description="查看EEG数据", response_model=Response[dict[str, Any]])
@wrap_api_response
def display_eeg(
    request: DisplayEEGRequest,
    ctx: Context = Depends(researcher_context),
    stub: EEGServiceStub = Depends(grpc_stub(EEGServiceStub)),
) -> dict[str, Any]:
    grpc_request = GrpcDisplayEEGRequest(**request.dict())
    file = common_crud.get_row_by_id(ctx.db, File, request.file_id)
    grpc_request.file_path = str(get_os_path(file.experiment_id, file.index, file.extension))
    grpc_request.file_type = file.extension
    grpc_response = stub.displayEEG(grpc_request)
    response_dict = serialize_protobuf(grpc_response)
    return response_dict
