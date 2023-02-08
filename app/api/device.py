from fastapi import APIRouter, Depends

from app.common.context import Context, researcher_context
from app.common.exception import ServiceError
from app.db import common_crud, crud
from app.db.orm import Device, Experiment
from app.model.request import CreateDeviceRequest
from app.model.response import Response, wrap_api_response

router = APIRouter(tags=["device"])


@router.post("/api/createDevice", description="创建设备", response_model=Response[int])
@wrap_api_response
def create_device(request: CreateDeviceRequest, ctx: Context = Depends(researcher_context)) -> int:
    database_error = ServiceError.database_fail("创建设备失败")

    # 检查实验没有被删除
    deleted_experiments = common_crud.get_deleted_rows(ctx.db, Experiment, [request.experiment_id])
    if deleted_experiments is None:
        raise database_error
    elif len(deleted_experiments) < 1:
        raise ServiceError.not_found("未找到实验")

    next_index = crud.get_next_device_index(ctx.db, request.experiment_id)
    device_dict = request.dict() | {"index": next_index}
    device_id = common_crud.insert_row(ctx.db, Device, device_dict, commit=True)
    if device_id is None:
        raise database_error
    return device_id
