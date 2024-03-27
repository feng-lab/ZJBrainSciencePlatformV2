from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from app.api import check_dataset_exists, wrap_api_response

import app.db.crud.eegdata as crud
from app.common.exception import ServiceError
from app.common.localization import Entity
from app.common.context import HumanSubjectContext, ResearcherContext

from app.db import common_crud
from app.db.orm import EEGData

from app.model import convert
from app.model.schema import CreateDatasetRequest, EEGDataInfo, EEGDataSearch, UpdateEEGDataRequest
from app.model.request import DeleteModelRequest
from app.model.response import NoneResponse, Page, Response

router = APIRouter(tags=["eegdata"])


@router.post("/api/createEEGData", description="创建数据集", response_model=Response[int])
@wrap_api_response
def create_eegdata(request: CreateDatasetRequest, ctx: ResearcherContext = Depends()) -> int:
    eegdata_dict = request.dict()
    eegdata_id = common_crud.insert_row(ctx.db, EEGData, eegdata_dict, commit=True)
    if eegdata_id is None:
        raise ServiceError.database_fail()
    return eegdata_id


@router.post("/api/getEEGDataInfo", description="获取数据集详情", response_model=Response[EEGDataInfo])
@wrap_api_response
def get_eegdata_info(eegdata_id: int, ctx: HumanSubjectContext = Depends()) -> EEGDataInfo:
    orm_EEGData = common_crud.get_row_by_id(ctx.db, EEGData, eegdata_id)
    if orm_EEGData is None:
        raise ServiceError.not_found(Entity.EEGData)
    eegdata_info = convert.EEGData_orm_2_info(orm_EEGData)
    return eegdata_info


@router.post("/api/getEEGDataByPag", description="获取数据集列表", response_model=Response[Page[EEGDataInfo]])
@wrap_api_response
def get_dataset_by_page(search: EEGDataSearch = Depends(), ctx: HumanSubjectContext = Depends()) -> Page[EEGDataInfo]:
    total, orm_eegdata = crud.search_eegdata(ctx.db, search)
    eegdata_infos = convert.map_list(convert.EEGData_orm_2_info, orm_eegdata)
    return Page(total=total, items=eegdata_infos)


@router.post("/api/updateEEGData", description="更新数据集", response_model=NoneResponse)
@wrap_api_response
def update_EEGData(request: UpdateEEGDataRequest, ctx: ResearcherContext = Depends()) -> None:
    orm_eegdata = common_crud.get_row_by_id(ctx.db, EEGData, request.id)
    if orm_eegdata is None:
        raise ServiceError.not_found(Entity.dataset)
    dataset_dict = request.dict(exclude_unset=True)
    success = common_crud.update_row(ctx.db, EEGData, dataset_dict, id_=request.id, commit=True)
    if not success:
        raise ServiceError.eegdata_fail()


@router.delete("/api/deleteEEGData", description="删除数据集", response_model=NoneResponse)
@wrap_api_response
def delete_dataset(request: DeleteModelRequest, ctx: ResearcherContext = Depends()) -> None:
    success = common_crud.bulk_update_rows_as_deleted(ctx.db, EEGData, ids=[request.id], commit=True)
    if not success:
        raise ServiceError.eegdata_fail()


