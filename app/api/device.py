from fastapi import APIRouter, Depends, Query

from app.api import check_device_exists, check_experiment_exists
from app.common.context import HumanSubjectContext, ResearcherContext
from app.common.exception import ServiceError
from app.db import common_crud, crud
from app.db.orm import Device
from app.model import convert
from app.model.request import DeleteModelRequest
from app.model.response import NoneResponse, PagedData, Response, wrap_api_response
from app.model.schema import CreateDeviceRequest, DeviceResponse, PageParm, UpdateDeviceRequest

router = APIRouter(tags=["device"])


@router.post("/api/createDevice", description="创建设备", response_model=Response[int])
@wrap_api_response
def create_device(request: CreateDeviceRequest, ctx: ResearcherContext = Depends()) -> int:
    check_experiment_exists(ctx.db, request.experiment_id)

    next_index = crud.get_next_device_index(ctx.db, request.experiment_id)
    device_dict = request.dict() | {"index": next_index}
    device_id = common_crud.insert_row(ctx.db, Device, device_dict, commit=True)
    if device_id is None:
        raise ServiceError.database_fail("创建设备失败")
    return device_id


@router.get("/api/getDeviceInfo", description="获取设备详情", response_model=Response[DeviceResponse])
@wrap_api_response
def get_device_info(
    device_id: int = Query(description="设备ID", ge=0), ctx: HumanSubjectContext = Depends()
) -> DeviceResponse:
    orm_device = common_crud.get_row_by_id(ctx.db, Device, device_id)
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
    page_param: PageParm = Depends(),
    ctx: HumanSubjectContext = Depends(),
) -> PagedData[DeviceResponse]:
    total, orm_devices = crud.search_devices(ctx.db, experiment_id, page_param)
    device_responses = convert.map_list(convert.device_orm_2_response, orm_devices)
    return PagedData(total=total, items=device_responses)


@router.post("/api/updateDevice", description="更新设备", response_model=NoneResponse)
@wrap_api_response
def update_device(request: UpdateDeviceRequest, ctx: ResearcherContext = Depends()) -> None:
    check_device_exists(ctx.db, request.id)

    update_dict = request.dict(exclude={"id"})
    success = common_crud.update_row(ctx.db, Device, update_dict, id=request.id, commit=True)
    if not success:
        raise ServiceError.database_fail("更新设备失败")


@router.delete("/api/deleteDevice", description="删除设备", response_model=NoneResponse)
@wrap_api_response
def delete_device(request: DeleteModelRequest, ctx: ResearcherContext = Depends()) -> None:
    success = common_crud.update_row_as_deleted(ctx.db, Device, id=request.id, commit=True)
    if not success:
        raise ServiceError.database_fail("删除设备失败")
