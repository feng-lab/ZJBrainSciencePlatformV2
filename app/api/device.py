from fastapi import APIRouter, Depends, Query

from app.common.context import Context, human_subject_context, researcher_context
from app.common.exception import ServiceError
from app.db import common_crud, crud
from app.db.orm import Device, Experiment
from app.model import convert
from app.model.request import DeleteModelRequest, GetModelsByPageParam, get_models_by_page
from app.model.response import NoneResponse, PagedData, Response, wrap_api_response
from app.model.schema import CreateDeviceRequest, DeviceResponse, UpdateDeviceRequest

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


@router.get("/api/getDeviceInfo", description="获取设备详情", response_model=Response[DeviceResponse])
@wrap_api_response
def get_device_info(
    device_id: int = Query(description="设备ID", ge=0), ctx: Context = Depends(human_subject_context)
) -> DeviceResponse:
    orm_device = common_crud.select_row_by_id(ctx.db, Device, device_id)
    if orm_device is None:
        raise ServiceError.not_found("未找到设备")
    device_response = convert.device_orm_2_response(orm_device)
    return device_response


@router.get(
    "/api/getDevicesByPage",
    description="分页获取设备详情",
    response_model=Response[PagedData[DeviceResponse]],
)
@wrap_api_response
def get_devices_by_page(
    experiment_id: int = Query(description="实验ID", default=0),
    page_param: GetModelsByPageParam = Depends(get_models_by_page),
    ctx: Context = Depends(human_subject_context),
) -> PagedData[DeviceResponse]:
    total, orm_devices = crud.search_devices(ctx.db, experiment_id, page_param)
    device_responses = convert.map_list(convert.device_orm_2_response, orm_devices)
    return PagedData(total=total, items=device_responses)


@router.post("/api/updateDevice", description="更新设备", response_model=NoneResponse)
@wrap_api_response
def update_device(request: UpdateDeviceRequest, ctx: Context = Depends(researcher_context)) -> None:
    database_fail = ServiceError.database_fail("更新设备失败")

    is_device_valid = common_crud.check_row_valid(ctx.db, Device, request.id)
    if is_device_valid is None:
        raise database_fail
    elif not is_device_valid:
        raise ServiceError.not_found("设备不存在")

    update_dict = request.dict(exclude={"id"})
    success = common_crud.update_row(ctx.db, Device, request.id, update_dict, commit=True)
    if not success:
        raise database_fail


@router.delete("/api/deleteDevice", description="删除设备", response_model=NoneResponse)
@wrap_api_response
def delete_device(request: DeleteModelRequest, ctx: Context = Depends(researcher_context)) -> None:
    success = common_crud.update_row_as_deleted(ctx.db, Device, request.id, commit=True)
    if not success:
        raise ServiceError.database_fail("删除设备失败")
