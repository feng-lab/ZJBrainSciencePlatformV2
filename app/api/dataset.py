from pathlib import PurePosixPath
from typing import Annotated, Dict, List
from urllib.parse import quote

from fastapi import APIRouter, Body, Depends, File, Form, Query, UploadFile
from fastapi.responses import StreamingResponse
from starlette.responses import guess_type
from zjbs_file_client import Client, FileType

import app.db.crud.dataset as crud
from app.api import check_dataset_exists, wrap_api_response
from app.common.config import config
from app.common.context import HumanSubjectContext, ResearcherContext
from app.common.exception import ServiceError
from app.common.localization import Entity
from app.db import common_crud
from app.db.orm import Dataset, DatasetFile
from app.model import convert
from app.model.request import DeleteModelRequest
from app.model.response import NoneResponse, Page, Response
from app.model.schema import (
    CreateDatasetRequest,
    DatasetDirectoryTreeNode,
    DatasetInfo,
    DatasetSearch,
    PageParm,
    UpdateDatasetRequest,
)

router = APIRouter(tags=["dataset"])


@router.post("/api/createDataset", description="创建数据集", response_model=Response[int])
@wrap_api_response
def create_dataset(request: CreateDatasetRequest, ctx: ResearcherContext = Depends()) -> int:
    dataset_dict = request.dict()
    dataset_id = common_crud.insert_row(ctx.db, Dataset, dataset_dict, commit=False)
    if dataset_id is None:
        raise ServiceError.database_fail()

    with Client(config.FILE_SERVER_URL) as client:
        file_server_response = client.inner.post(
            "/create-directory", params={"path": dataset_file_path(dataset_id, "/"), "exists_ok": True}
        )
        if not file_server_response.is_success:
            raise ServiceError.remote_service_error(file_server_response.reason_phrase)

    ctx.db.commit()
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


@router.get("/api/getDatasetSize", description="获取单个数据集大小", response_model=Response[int])
@wrap_api_response
def get_dataset_size(dataset_id: int, ctx: HumanSubjectContext = Depends()) -> int:
    check_dataset_exists(ctx.db, dataset_id)
    with Client(config.FILE_SERVER_URL) as client:
        file_server_response = client.inner.get("/get-size", params={"path": dataset_file_path(dataset_id, "/")})
        if file_server_response.status_code != 200:
            raise ServiceError.remote_service_error(file_server_response.text)
        return file_server_response.json()


@router.get("/api/getAllDatasetSize", description="获取数据集大小", response_model=Response[int])
@wrap_api_response
def get_all_datasets_size(ctx: HumanSubjectContext = Depends()) -> int:
    dataset_ids = common_crud.get_all_ids(ctx.db, Dataset)
    dataset_size = 0
    with Client(config.FILE_SERVER_URL) as client:
        for dataset_id in dataset_ids:
            file_server_response = client.inner.get("/get-size", params={"path": dataset_file_path(dataset_id, "/")})
            if file_server_response.status_code != 200:
                raise ServiceError.remote_service_error(file_server_response.text)
            file_server_response_value = file_server_response.json()
            dataset_size += file_server_response_value
    return dataset_size


@router.get("/api/getGroupDatasetSize", description="获取分组数据集大小", response_model=Response[dict])
@wrap_api_response
def get_group_dataset_size(search: str, ctx: HumanSubjectContext = Depends()) -> list[dict[str, int]]:
    fin_size = []
    species_id_mapping = crud.get_species_ids_mapping(ctx.db, search)
    with Client(config.FILE_SERVER_URL) as client:
        for key, dataset_ids in species_id_mapping.items():
            species_counts = len(dataset_ids)
            dataset_size = 0
            for dataset_id in dataset_ids:
                file_server_response = client.inner.get(
                    "/get-size", params={"path": dataset_file_path(dataset_id, "/")}
                )
                if file_server_response.status_code != 200:
                    raise ServiceError.remote_service_error(file_server_response.text)
                file_server_response_value = file_server_response.json()
                dataset_size += file_server_response_value
            fin_size.append({"name": key, "dataset_size": dataset_size, "counts": species_counts})
    return fin_size


@router.get("/api/getGroupCells", description="获取分组细胞数目", response_model=Response[dict])
@wrap_api_response
def get_group_cells(search: str, ctx: HumanSubjectContext = Depends()) -> list[dict[str, int]]:
    return crud.get_species_cells_mapping(ctx.db, search)


@router.get("/api/getDataSizePerMouth", description="获取每月数据量", response_model=Response[list])
@wrap_api_response
def get_data_size_per_mouth(ctx: HumanSubjectContext = Depends()):
    total, orm_datasets_collection = crud.get_dataset_size_month(ctx.db)
    dataset_infos = convert.map_list(convert.cumulative_dataset_size_2_info, orm_datasets_collection)

    return Page(total=total, items=dataset_infos)


@router.get("/api/getDatasetCollectionInfo", description="获取数据收集信息", response_model=Response[list])
@wrap_api_response
def get_dataset_collection_info(search: PageParm = Depends(), ctx: HumanSubjectContext = Depends()):
    total, orm_datasets = crud.get_dataset_collection_info(ctx.db, search)
    new_orm_datasets = []
    with Client(config.FILE_SERVER_URL) as client:
        for dataset_row in orm_datasets:
            datset_id = dataset_row[0]
            file_server_response = client.inner.get("/get-size", params={"path": dataset_file_path(datset_id, "/")})
            if file_server_response.status_code != 200:
                raise ServiceError.remote_service_error(file_server_response.text)
            file_server_response_value = file_server_response.json()
            new_orm_datasets.append((dataset_row, file_server_response_value))
    dataset_collection_infos = convert.map_list(convert.dataset_collection_2_info, new_orm_datasets)
    return Page(total=total, items=dataset_collection_infos)


@router.delete("/api/deleteDataset", description="删除数据集", response_model=NoneResponse)
@wrap_api_response
def delete_dataset(request: DeleteModelRequest, ctx: ResearcherContext = Depends()) -> None:
    success = common_crud.bulk_update_rows_as_deleted(ctx.db, Dataset, ids=[request.id], commit=True)
    if not success:
        raise ServiceError.database_fail()


@router.post("/api/CheckDatasetDir", description="检查数据条目", response_model=NoneResponse)
@wrap_api_response
def check_dataset_dir(ctx: ResearcherContext = Depends()) -> None:
    dataset_ids = common_crud.get_all_ids(ctx.db, Dataset)
    with Client(config.FILE_SERVER_URL) as client:
        for dataset_id in dataset_ids:
            print(dataset_file_path(dataset_id, "/"))
            file_server_response = client.inner.post(
                "/create-directory", params={"path": dataset_file_path(dataset_id, "/"), "exists_ok": True}
            )
            if not file_server_response.is_success:
                raise ServiceError.remote_service_error(file_server_response.reason_phrase)
    ctx.db.commit()


def dataset_file_path(dataset_id: int, *parts: str) -> PurePosixPath:
    file_path = PurePosixPath(f"/dataset_{dataset_id}")
    for part in parts:
        file_path = file_path / part.lstrip("/")
    return file_path


@router.post("/api/uploadDatasetFile", description="上传数据集文件", response_model=NoneResponse)
@wrap_api_response
def upload_dataset_file(
    dataset_id: Annotated[int, Form(description="数据集ID")],
    directory: Annotated[str, Form(description="目标文件夹路径")],
    file: Annotated[UploadFile, File(description="文件")],
    ctx: ResearcherContext = Depends(),
) -> None:
    check_dataset_exists(ctx.db, dataset_id)
    directory_path = dataset_file_path(dataset_id, directory)
    with Client(config.FILE_SERVER_URL) as client:
        client.upload(str(directory_path), file.file, file.filename, mkdir=True, allow_overwrite=True)

    success = common_crud.insert_row(
        ctx.db, DatasetFile, {"dataset_id": dataset_id, "path": str(directory_path)}, commit=True
    )
    if not success:
        raise ServiceError.database_fail()


@router.get("/api/downloadDatasetFile", description="下载数据集文件")
def download_dataset_file(
    dataset_id: Annotated[int, Query(description="数据集ID")],
    path: Annotated[str, Query(description="文件路径")],
    ctx: HumanSubjectContext = Depends(),
) -> StreamingResponse:
    check_dataset_exists(ctx.db, dataset_id)
    file_path = dataset_file_path(dataset_id, path)
    with Client(config.FILE_SERVER_URL) as client:
        file_server_response = client.inner.post("/download-file", params={"path": str(file_path)})
        if file_server_response.status_code != 200:
            raise ServiceError.remote_service_error(file_server_response.text)
        return StreamingResponse(
            file_server_response.iter_bytes(1024),
            headers={
                "Content-Disposition": f'attachment; filename="{quote(file_path.name)}"',
                "Content-Type": guess_type(file_path.name)[0] or "text/plain",
            },
        )


@router.get("/api/listDatasetFiles", description="获取数据集文件列表")
@wrap_api_response
def list_dataset_files(
    dataset_id: Annotated[int, Query(description="数据集ID")],
    directory: Annotated[str, Query(description="文件夹路径")],
    ctx: HumanSubjectContext = Depends(),
):
    check_dataset_exists(ctx.db, dataset_id)
    directory_path = dataset_file_path(dataset_id, directory)
    with Client(config.FILE_SERVER_URL) as client:
        file_server_response = client.inner.post("/list-directory", params={"directory": str(directory_path)})
        if file_server_response.status_code != 200:
            raise ServiceError.remote_service_error(file_server_response.text)
        return file_server_response.json()


@router.get(
    "/api/getDatasetDirectoryTree",
    description="获取数据集文件树（仅包括文件夹）",
    response_model=Response[list[DatasetDirectoryTreeNode]],
)
@wrap_api_response
def list_dataset_directory_tree(
    dataset_id: int = Query(description="数据集ID", ge=0), ctx: HumanSubjectContext = Depends()
) -> list[DatasetDirectoryTreeNode]:
    check_dataset_exists(ctx.db, dataset_id)
    with Client(config.FILE_SERVER_URL) as client:
        return walk_dataset_directory_tree(dataset_file_path(dataset_id, "/"), client)


def walk_dataset_directory_tree(root: PurePosixPath, client: Client) -> list[DatasetDirectoryTreeNode]:
    return [
        DatasetDirectoryTreeNode(name=item.name, dirs=walk_dataset_directory_tree(root / item.name, client))
        for item in client.list_directory(str(root))
        if item.type == FileType.directory
    ]


@router.post("/api/renameDatasetFile", description="重命名数据集文件", response_model=NoneResponse)
@wrap_api_response
def rename_dataset_file(
    dataset_id: Annotated[int, Body(description="数据集ID")],
    path: Annotated[str, Body(description="文件路径")],
    new_name: Annotated[str, Body(description="新文件名")],
    ctx: ResearcherContext = Depends(),
) -> None:
    check_dataset_exists(ctx.db, dataset_id)
    path = dataset_file_path(dataset_id, path)
    with Client(config.FILE_SERVER_URL) as client:
        client.rename(str(path), new_name)

    success = common_crud.update_row(
        ctx.db,
        DatasetFile,
        {"path": str(path.with_name(new_name))},
        where=[DatasetFile.dataset_id == dataset_id],
        commit=True,
    )
    if not success:
        raise ServiceError.database_fail()


@router.delete("/api/deleteDatasetFile", description="删除数据集文件", response_model=NoneResponse)
@wrap_api_response
def delete_dataset_file(
    dataset_id: Annotated[int, Body(description="数据集ID")],
    path: Annotated[str, Body(description="文件路径")],
    ctx: ResearcherContext = Depends(),
) -> None:
    check_dataset_exists(ctx.db, dataset_id)
    path = dataset_file_path(dataset_id, path)
    with Client(config.FILE_SERVER_URL) as client:
        client.delete(str(path))

    success = common_crud.update_row_as_deleted(
        ctx.db, DatasetFile, where=[DatasetFile.dataset_id == dataset_id, DatasetFile.path == path], commit=True
    )
    if not success:
        raise ServiceError.database_fail()
