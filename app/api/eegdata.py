from pathlib import PurePosixPath
from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, Body, Depends, File, Form, Query, UploadFile
from fastapi.responses import StreamingResponse
from zjbs_file_client import Client

import app.db.crud.eegdata as crud
from app.api import check_eegdata_exists, wrap_api_response
from app.common.exception import ServiceError
from app.common.localization import Entity
from app.common.context import HumanSubjectContext, ResearcherContext
from app.common.config import config
from app.db import common_crud
from app.db.orm import EEGData

from app.model import convert
from app.model.schema import CreateEEGDataRequest, EEGDataInfo, EEGDataSearch, UpdateEEGDataRequest
from app.model.request import DeleteModelRequest
from app.model.response import NoneResponse, Page, Response

router = APIRouter(tags=["eeg_data"])


@router.post("/api/createEEGData", description="创建数据集", response_model=Response[int])
@wrap_api_response
def create_eeg_data(request: CreateEEGDataRequest, ctx: ResearcherContext = Depends()) -> int:
    eeg_data_dict = request.dict()
    eeg_data_id = common_crud.insert_row(ctx.db, EEGData, eeg_data_dict, commit=True)
    if eeg_data_id is None:
        raise ServiceError.database_fail()
    return eeg_data_id


@router.get("/api/getEEGDataInfo", description="获取数据集详情", response_model=Response[EEGDataInfo])
@wrap_api_response
def get_eeg_data_info(eeg_data_id: int, ctx: HumanSubjectContext = Depends()) -> EEGDataInfo:
    orm_eeg_data = common_crud.get_row_by_id(ctx.db, EEGData, eeg_data_id)
    if orm_eeg_data is None:
        raise ServiceError.not_found(Entity.eeg_data)
    eeg_data_info = convert.EEGData_orm_2_info(orm_eeg_data)
    return eeg_data_info


@router.get("/api/getEEGDataByPag", description="获取数据集列表", response_model=Response[Page[EEGDataInfo]])
@wrap_api_response
def get_eeg_data_by_page(search: EEGDataSearch = Depends(), ctx: HumanSubjectContext = Depends()) -> Page[EEGDataInfo]:
    total, orm_eeg_data = crud.search_eegdata(ctx.db, search)
    eeg_data_infos = convert.map_list(convert.EEGData_orm_2_info, orm_eeg_data)
    return Page(total=total, items=eeg_data_infos)


@router.post("/api/updateEEGData", description="更新数据集", response_model=NoneResponse)
@wrap_api_response
def update_eeg_data(request: UpdateEEGDataRequest, ctx: ResearcherContext = Depends()) -> None:
    orm_eeg_data = common_crud.get_row_by_id(ctx.db, EEGData, request.id)
    if orm_eeg_data is None:
        raise ServiceError.not_found(Entity.eeg_data)
    dataset_dict = request.dict(exclude_unset=True)
    success = common_crud.update_row(ctx.db, EEGData, dataset_dict, id_=request.id, commit=True)
    if not success:
        raise ServiceError.database_fail()


@router.delete("/api/deleteEEGData", description="删除数据集", response_model=NoneResponse)
@wrap_api_response
def delete_eeg_data(request: DeleteModelRequest, ctx: ResearcherContext = Depends()) -> None:
    success = common_crud.bulk_update_rows_as_deleted(ctx.db, EEGData, ids=[request.id], commit=True)
    if not success:
        raise ServiceError.database_fail()


def eeg_data_file_path(eeg_data_id: int, *parts: str) -> PurePosixPath:
    file_path = PurePosixPath(f"/eeg_data_{eeg_data_id}")
    for part in parts:
        file_path = file_path / part.lstrip("/")
    return file_path


@router.post("/api/uploadEEGDataFile", description="上传脑电数据文件", response_model=NoneResponse)
@wrap_api_response
def upload_eeg_data_file(
    eeg_data_id: Annotated[int, Form(description="脑电数据ID")],
    directory: Annotated[str, Form(description="目标文件夹路径")],
    file: Annotated[UploadFile, File(description="文件")],
    ctx: ResearcherContext = Depends(),
) -> None:
    check_eegdata_exists(ctx.db, eeg_data_id)
    directory_path = eeg_data_file_path(eeg_data_id, directory)
    with Client(config.FILE_SERVER_URL) as client:
        client.upload(str(directory_path), file.file, file.filename, mkdir=True, allow_overwrite=True)


@router.get("/api/downloadEEGDataFile", description="下载脑电数据文件")
def download_eeg_data_file(
    eeg_data_id: Annotated[int, Query(description="脑电数据ID")],
    path: Annotated[str, Query(description="文件路径")],
    ctx: HumanSubjectContext = Depends(),
) -> StreamingResponse:
    check_eegdata_exists(ctx.db, eeg_data_id)
    file_path = eeg_data_file_path(eeg_data_id,path)
    with Client(config.FILE_SERVER_URL) as client:
        file_server_response = client.inner.post("/download-file", params={"path": str(file_path)})
        if file_server_response.status_code != 200:
            raise ServiceError.remote_service_error(file_server_response.text)
        return StreamingResponse(
            file_server_response.iter_bytes(1024),
            headers={"Content-Disposition": f"attachment; filename={quote(file_path.name)}"},
        )


@router.delete("/api/deleteEEGDataFile", description="删除脑电文件", response_model=NoneResponse)
@wrap_api_response
def delete_eeg_data_file(
    eeg_data_id: Annotated[int, Body(description="脑电数据ID")],
    path: Annotated[str, Body(description="文件路径")],
    ctx: ResearcherContext = Depends(),
) -> None:
    check_eegdata_exists(ctx.db, eeg_data_id)
    path = eeg_data_file_path(eeg_data_id, path)
    with Client(config.FILE_SERVER_URL) as client:
        client.delete(str(path))
