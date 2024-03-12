from fastapi import APIRouter, Depends

import app.db.crud.dataset as crud
from app.api import wrap_api_response
from app.common.context import HumanSubjectContext, ResearcherContext
from app.common.exception import ServiceError
from app.common.localization import Entity
from app.db import common_crud
from app.db.orm import Dataset
from app.model import convert
from app.model.response import NoneResponse, Page, Response
from app.model.schema import CreateDatasetRequest, DatasetInfo, DatasetSearch, UpdateDatasetRequest

router = APIRouter(tags=["dataset"])


@router.post("/api/createDataset", description="创建数据集", response_model=Response[int])
@wrap_api_response
def create_dataset(request: CreateDatasetRequest, ctx: ResearcherContext = Depends()) -> int:
    dataset_dict = request.dict()
    dataset_id = common_crud.insert_row(ctx.db, Dataset, dataset_dict, commit=True)
    if dataset_id is None:
        raise ServiceError.database_fail()
    return dataset_id


@router.post("/api/getDatasetInfo", description="获取数据集详情", response_model=Response[DatasetInfo])
@wrap_api_response
def get_dataset_info(dataset_id: int, ctx: HumanSubjectContext = Depends()) -> DatasetInfo:
    orm_dataset = common_crud.get_row_by_id(ctx.db, Dataset, dataset_id)
    if orm_dataset is None:
        raise ServiceError.not_found(Entity.dataset)
    dataset_info = convert.dataset_orm_2_info(orm_dataset)
    return dataset_info


@router.post("/api/getDatasetByPage", description="获取数据集列表", response_model=Response[Page[DatasetInfo]])
@wrap_api_response
def get_dataset_by_page(search: DatasetSearch = Depends(), ctx: HumanSubjectContext = Depends()) -> Page[DatasetInfo]:
    total, orm_datasets = crud.search_datasets(ctx.db, search)
    dataset_infos = convert.map_list(convert.dataset_orm_2_info, orm_datasets)
    return Page(total=total, items=dataset_infos)


@router.post("/api/updateDataset", description="更新数据集", response_model=NoneResponse)
@wrap_api_response
def update_dataset(request: UpdateDatasetRequest, ctx: ResearcherContext = Depends()) -> None:
    orm_dataset = common_crud.get_row_by_id(ctx.db, Dataset, request.id)
    if orm_dataset is None:
        raise ServiceError.not_found(Entity.dataset)
    dataset_dict = request.dict(exclude_unset=True)
    success = common_crud.update_row(ctx.db, Dataset, dataset_dict, id_=request.id, commit=True)
    if not success:
        raise ServiceError.database_fail()


@router.delete("/api/deleteDataset", description="删除数据集", response_model=NoneResponse)
@wrap_api_response
def delete_dataset(dataset_id: int, ctx: ResearcherContext = Depends()) -> None:
    success = common_crud.bulk_update_rows_as_deleted(ctx.db, Dataset, ids=[dataset_id], commit=True)
    if not success:
        raise ServiceError.database_fail()
