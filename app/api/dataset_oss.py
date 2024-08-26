import os.path
from pathlib import PurePosixPath
from typing import Annotated

from fastapi import APIRouter, Body, Depends, File, Form, Query, UploadFile
from fastapi.responses import StreamingResponse

import app.db.crud.dataset as crud
from app.api import check_dataset_exists, wrap_api_response
from app.common.config import config
from app.common.context import HumanSubjectContext, ResearcherContext
from app.common.exception import ServiceError
from app.common.oss_base import (
    bucket_auth,
    create_dir,
    delete_object_oss,
    object_ls,
    object_size_Byte,
    oos_file_upload,
    rename_object,
    stream_download,
)
from app.common.localization import Entity
from app.db import common_crud
from app.db.orm import Dataset, DatasetFile
from app.model import convert
from app.model.response import NoneResponse, Page, Response
from app.model.schema import CreateDatasetRequest, PageParm,CreateDatasetFileRequest,UpdateDatasetFileRequest

router = APIRouter(tags=["dataset_oss"])


@router.post("/api/createDatasetOss", description="创建oss数据集", response_model=Response[int])
@wrap_api_response
def create_dataset_oss(request: CreateDatasetRequest, ctx: ResearcherContext = Depends()) -> int:
    dataset_dict = request.dict()
    dataset_id = common_crud.insert_row(ctx.db, Dataset, dataset_dict, commit=False)
    if dataset_id is None:
        raise ServiceError.database_fail()
    create_dir(bucket_auth(), dataset_file_path(dataset_id, "/"))
    ctx.db.commit()
    return dataset_id


def dataset_file_path(dataset_id: int | None, *parts: str) -> str:
    file_path = PurePosixPath(config.OSS_FILE_DIR, f"dataset_{dataset_id}/")
    for part in parts:
        file_path = file_path / part.lstrip("/")
    if part.endswith("/"):
        file_path = file_path.as_posix() + "/"
    return file_path


@router.get("/api/getDatasetSizeOss", description="获取oss单个数据集大小", response_model=Response[float])
@wrap_api_response
def get_dataset_size_oss(dataset_id: int, from_table: bool = True, ctx: HumanSubjectContext = Depends()) -> float:
    check_dataset_exists(ctx.db, dataset_id)
    if from_table:
        file_size = crud.get_size_by_id(ctx.db, dataset_id)
    else:
        file_size = object_size_Byte(bucket_auth(), remote_fp=dataset_file_path(dataset_id, "/"))
        file_size = file_size / 1024 / 1024 / 1024
    return file_size


@router.get("/api/getAllDatasetSizeOss", description="获取oss所有数据集大小", response_model=Response[float])
@wrap_api_response
def get_all_datasets_size_oss(from_table: bool = True, ctx: HumanSubjectContext = Depends()) -> float:
    if from_table:
        dataset_size = crud.get_sizes_all(ctx.db)
    else:
        oss_path = str(PurePosixPath(config.OSS_FILE_DIR / ""))
        dataset_size = object_size_Byte(bucket_auth(), remote_fp=oss_path)
        dataset_size = dataset_size / 1024 / 1024 / 1024
    return dataset_size


@router.get("/api/getGroupDatasetSizeOss", description="获取oss分组数据集大小", response_model=Response[dict])
@wrap_api_response
def get_group_dataset_size_oss(
    search: str, from_table: bool = True, ctx: HumanSubjectContext = Depends()
) -> list[dict[str, int]]:
    if from_table:
        fin_size = crud.get_species_cells_mapping_oss(ctx.db, search)
    else:
        fin_size = []
        species_id_mapping = crud.get_species_ids_mapping(ctx.db, search)
        for key, dataset_ids in species_id_mapping.items():
            species_counts = len(dataset_ids)
            dataset_size = 0
            for dataset_id in dataset_ids:
                files_size = object_size_Byte(bucket_auth(), remote_fp=dataset_file_path(dataset_id, "/"))
                files_size = files_size / 1024 / 1024 / 1024
                dataset_size += files_size
            fin_size.append({"name": key, "dataset_size": dataset_size, "counts": species_counts})
    return fin_size


@router.get("/api/getDatasetCollectionInfoOss", description="获取oss数据收集信息", response_model=Response[list])
@wrap_api_response
def get_dataset_collection_info_oss(
    search: PageParm = Depends(), from_table: bool = True, ctx: HumanSubjectContext = Depends(), is_order: bool = True
):
    if from_table:
        total, orm_datasets = crud.get_dataset_collection_info_oss_table(ctx.db, search, is_order)
        dataset_collection_infos = convert.map_list(convert.dataset_collection_oss_table_2_info, orm_datasets)
    else:
        total, orm_datasets = crud.get_dataset_collection_info(ctx.db, search, is_order)
        new_orm_datasets = []
        for dataset_row in orm_datasets:
            dataset_id = dataset_row[0]
            file_size = object_size_Byte(bucket_auth(), remote_fp=dataset_file_path(dataset_id, "/"))
            file_size = file_size / 1024 / 1024 / 1024
            new_orm_datasets.append((dataset_row, file_size))
        dataset_collection_infos = convert.map_list(convert.dataset_collection_2_info, new_orm_datasets)
    return Page(total=total, items=dataset_collection_infos)


@router.post("/api/uploadDatasetFileOss", description="上传oss数据集文件", response_model=NoneResponse)
@wrap_api_response
def upload_dataset_file_oss(
    dataset_id: Annotated[int, Form(description="数据集ID")],
    directory: Annotated[str, Form(description="目标文件夹路径")],
    file: Annotated[UploadFile, File(description="文件")],
    ctx: ResearcherContext = Depends(),
) -> None:
    check_dataset_exists(ctx.db, dataset_id)
    directory_path = dataset_file_path(dataset_id, directory, file.filename)
    file_type = directory.split(".")[-1].lower()
    file_size = file.size
    oos_file_upload(bucket_auth(), remote_fp=str(directory_path), reader=file.file, file_size=file_size)
    success = common_crud.insert_row(
        ctx.db,
        DatasetFile,
        {
            "dataset_id": dataset_id,
            "oss_path": str(directory_path),
            "file_size": float(file_size),
            "file_format": str(file_type),
        },
        commit=True,
    )
    if not success:
        raise ServiceError.database_fail()


@router.get("/api/listDatasetFilesOss", description="获取oss数据集文件列表", response_model=Response[list[dict[str, int]]])
@wrap_api_response
def list_dataset_files(
    dataset_id: Annotated[int, Query(description="数据集ID")],
    directory: Annotated[str, Query(description="文件夹路径")],
    file_type: Annotated[str, Query(description="文件夹路径")] = None,
    ctx: HumanSubjectContext = Depends(),
) -> list[dict[str, int]]:
    check_dataset_exists(ctx.db, dataset_id)
    directory_path = dataset_file_path(dataset_id, directory)
    files = object_ls(bucket_auth(), str(directory_path))

    if file_type is None:
        return [{"counts": len(files)}, files]
    else:
        filtered_files = [f for f in files if f.get("name").endswith(f".{file_type}")]
        return [{"counts": len(filtered_files)}, filtered_files]


@router.get("/api/downloadDatasetFileOss", description="下载oss数据集文件")
def download_dataset_file_oss(
    dataset_id: Annotated[int, Query(description="数据集ID")],
    path: Annotated[str, Query(description="文件路径")],
    ctx: ResearcherContext = Depends(),
) -> StreamingResponse:
    check_dataset_exists(ctx.db, dataset_id)
    file_path = dataset_file_path(dataset_id, path)
    file_server_response = stream_download(bucket_auth(), remote_fp=file_path)
    file_name = file_server_response.headers["Content-Disposition"]
    content_type = file_server_response.headers["Content-Type"] or "text/plain"
    return StreamingResponse(
        iter(lambda: file_server_response.read(1024), b""),
        headers={"Content-Disposition": file_name, "Content-Type": content_type},
    )


@router.post("/api/renameDatasetFileOss", description="重命名oss数据集文件", response_model=NoneResponse)
@wrap_api_response
def rename_dataset_file_oss(
    dataset_id: Annotated[int, Body(description="数据集ID")],
    path: Annotated[str, Body(description="文件路径")],
    new_name: Annotated[str, Body(description="新文件名")],
    ctx: ResearcherContext = Depends(),
) -> None:
    check_dataset_exists(ctx.db, dataset_id)
    path = dataset_file_path(dataset_id, path)
    new_path = dataset_file_path(dataset_id, new_name)
    rename_object(bucket_auth(), str(path), str(new_path))
    # 数据库表要更新
    success = common_crud.update_row(
        ctx.db,
        DatasetFile,
        {"other_path": str(path.with_name(new_name))},
        where=[DatasetFile.dataset_id == dataset_id],
        commit=True,
    )
    if not success:
        raise ServiceError.database_fail()


@router.delete("/api/deleteDatasetFileOss", description="删除数据集文件", response_model=NoneResponse)
@wrap_api_response
def delete_dataset_file_oss(
    dataset_id: Annotated[int, Body(description="数据集ID")],
    path: Annotated[str, Body(description="文件路径")],
    ctx: ResearcherContext = Depends(),
) -> None:
    check_dataset_exists(ctx.db, dataset_id)
    path = dataset_file_path(dataset_id, path)
    delete_object_oss(bucket_auth(), str(path))

    success = common_crud.update_row_as_deleted(
        ctx.db, DatasetFile, where=[DatasetFile.dataset_id == dataset_id, DatasetFile.oss_path == path], commit=True
    )
    if not success:
        raise ServiceError.database_fail()


@router.post("/api/createDatasetFile", description="创建数据集文件", response_model=Response[int])
@wrap_api_response
def create_dataset_file(request: CreateDatasetFileRequest, ctx: ResearcherContext = Depends()) -> int:
    dataset_file_dict = request.dict()
    dataset_file_id = common_crud.insert_row(ctx.db, DatasetFile, dataset_file_dict, commit=False)
    if dataset_file_id is None:
        raise ServiceError.database_fail()
    ctx.db.commit()
    return dataset_file_id


@router.post("/api/updateDatasetFile",description = '数据路径更新',response_model = NoneResponse)
@wrap_api_response
def update_dataset_file(request:UpdateDatasetFileRequest, ctx: ResearcherContext = Depends())-> None:
    orm_dataset_file = common_crud.get_row_by_id(ctx.db, DatasetFile, request.id)
    if orm_dataset_file is None:
        raise ServiceError.not_found(Entity.dataset)
    dataset_file_dict = request.dict(exclude_unset=True)
    success = common_crud.update_row(ctx.db, DatasetFile, dataset_file_dict, id_=request.id, commit=True)
    if not success:
        raise ServiceError.database_fail()


