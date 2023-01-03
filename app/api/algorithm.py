from fastapi import APIRouter, Depends

from app.common.context import Context, researcher_context
from app.common.depend import grpc_stub
from app.common.util import protobuf_to_pydantic
from app.grpc.eeg_pb2 import DisplayEEGRequest as GrpcDisplayEEGRequest
from app.grpc.eeg_pb2_grpc import EEGServiceStub
from app.model.request import DisplayEEGRequest
from app.model.response import DisplayEEGData, Response

router = APIRouter(tags=["algorithm"])


@router.post("/api/displayEEG", description="查看EEG数据", response_model=Response[DisplayEEGData])
def display_eeg(
    request: DisplayEEGRequest,
    _ctx: Context = Depends(researcher_context),
    stub: EEGServiceStub = Depends(grpc_stub(EEGServiceStub)),
) -> DisplayEEGData:
    grpc_request = GrpcDisplayEEGRequest(**request.dict())
    grpc_response = stub.displayEEG(grpc_request)
    response = protobuf_to_pydantic(grpc_response, DisplayEEGData)
    return response
