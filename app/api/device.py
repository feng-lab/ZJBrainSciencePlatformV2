import itertools

from fastapi import APIRouter, Depends, Query

import app.db.crud.device as crud
from app.api import check_device_exists, check_experiment_exists
from app.common.context import HumanSubjectContext, ResearcherContext
from app.common.exception import ServiceError
from app.db import common_crud
from app.db.orm import Device, ExperimentDevice
from app.model import convert
from app.model.request import DeleteDevicesRequest, UpdateDevicesInExperimentRequest
from app.model.response import NoneResponse, Page, Response, wrap_api_response
from app.model.schema import (
    CreateDeviceRequest,
    DeviceInfo,
    DeviceInfoWithIndex,
    DeviceSearch,
    UpdateDeviceRequest,
)

router = APIRouter(tags=["device"])


@router.post("/api/createDevice", description="创建设备", response_model=Response[int])
@wrap_api_response
def create_device(request: CreateDeviceRequest, ctx: ResearcherContext = Depends()) -> int:
    device_dict = request.dict()
    device_id = common_crud.insert_row(ctx.db, Device, device_dict, commit=True)
    if device_id is None:
        raise ServiceError.database_fail("创建设备失败")
    return device_id


@router.delete("/api/deleteDevices", description="批量删除设备", response_model=NoneResponse)
@wrap_api_response
def delete_device(request: DeleteDevicesRequest, ctx: ResearcherContext = Depends()) -> None:
    success = common_crud.bulk_update_rows_as_deleted(
        ctx.db, Device, ids=request.device_ids, commit=True
    )
    if not success:
        raise ServiceError.database_fail("删除设备失败")


@router.post("/api/addDevicesInExperiment", description="将设备添加到实验中", response_model=NoneResponse)
@wrap_api_response
def add_devices_in_experiment(
    request: UpdateDevicesInExperimentRequest, ctx: ResearcherContext = Depends()
) -> None:
    check_experiment_exists(ctx.db, request.experiment_id)

    add_device_ids = set(
        crud.filter_experiment_devices_to_add(ctx.db, request.experiment_id, request.device_ids)
    )
    if len(add_device_ids) > 0:
        last_index = crud.get_last_index(ctx.db, request.experiment_id)
        add_devices = [
            {"experiment_id": request.experiment_id, "device_id": device_id, "index": index}
            for device_id, index in zip(
                add_device_ids,
                itertools.count(start=(last_index + 1 if last_index is not None else 1), step=1),
            )
        ]
        success = common_crud.bulk_insert_rows(ctx.db, ExperimentDevice, add_devices, commit=True)
        if not success:
            raise ServiceError.database_fail("添加实验设备失败")


@router.delete(
    "/api/deleteDevicesFromExperiment", description="从设备中删除设备", response_model=NoneResponse
)
@wrap_api_response
def delete_devices_from_experiment(
    request: UpdateDevicesInExperimentRequest, ctx: ResearcherContext = Depends()
) -> None:
    check_experiment_exists(ctx.db, request.experiment_id)

    success = common_crud.bulk_delete_rows(
        ctx.db,
        ExperimentDevice,
        [
            ExperimentDevice.experiment_id == request.experiment_id,
            ExperimentDevice.device_id.in_(request.device_ids),
        ],
        commit=True,
    )
    if not success:
        raise ServiceError.database_fail("从设备中删除设备失败")


@router.get("/api/getDeviceInfo", description="获取设备详情", response_model=Response[DeviceInfo])
@wrap_api_response
def get_device_info(
    device_id: int = Query(description="设备ID", ge=0), ctx: HumanSubjectContext = Depends()
) -> DeviceInfo:
    orm_device = common_crud.get_row_by_id(ctx.db, Device, device_id)
    if orm_device is None:
        raise ServiceError.not_found("未找到设备")
    device_info = convert.device_orm_2_info(orm_device)
    return device_info


@router.get(
    "/api/getDevicesByPage",
    description="分页获取设备详情",
    response_model=Response[Page[DeviceInfoWithIndex]],
)
@wrap_api_response
def get_devices_by_page(
    search: DeviceSearch = Depends(), ctx: HumanSubjectContext = Depends()
) -> Page[DeviceInfoWithIndex]:
    total, orm_devices = crud.search_devices(ctx.db, search)
    device_infos = convert.map_list(convert.device_search_row_2_info_with_index, orm_devices)
    return Page(total=total, items=device_infos)


@router.post("/api/updateDevice", description="更新设备", response_model=NoneResponse)
@wrap_api_response
def update_device(request: UpdateDeviceRequest, ctx: ResearcherContext = Depends()) -> None:
    check_device_exists(ctx.db, request.id)

    update_dict = request.dict(exclude={"id"})
    success = common_crud.update_row(ctx.db, Device, update_dict, id=request.id, commit=True)
    if not success:
        raise ServiceError.database_fail("更新设备失败")
