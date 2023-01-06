from fastapi import APIRouter, Depends

from app.api.file import get_os_path
from app.common.context import Context, researcher_context
from app.common.depend import grpc_stub
from app.common.util import protobuf_to_pydantic
from app.db import crud
from app.db.orm import File
from app.grpc.eeg_pb2 import DisplayEEGRequest as GrpcDisplayEEGRequest
from app.grpc.eeg_pb2_grpc import EEGServiceStub
from app.model.request import DisplayEEGRequest
from app.model.response import DisplayEEGData, Response
from app.model.schema import FileInDB

router = APIRouter(tags=["algorithm"])


@router.post("/api/displayEEG", description="查看EEG数据", response_model=Response[DisplayEEGData])
def display_eeg(
    request: DisplayEEGRequest,
    ctx: Context = Depends(researcher_context),
    stub: EEGServiceStub = Depends(grpc_stub(EEGServiceStub)),
) -> DisplayEEGData:
    grpc_request = GrpcDisplayEEGRequest(**request.dict())
    file_in_db: FileInDB = crud.get_model(ctx.db, File, FileInDB, request.file_id)
    grpc_request.file_path = get_os_path(
        file_in_db.experiment_id, file_in_db.index, file_in_db.extension
    )
    grpc_request.file_type = file_in_db.extension
    grpc_response = stub.displayEEG(grpc_request)
    response = protobuf_to_pydantic(grpc_response, DisplayEEGData)
    return response
