from fastapi import APIRouter, Depends, Query

from app.api.file import delete_os_file, get_os_path
from app.common.context import Context, human_subject_context, researcher_context
from app.common.exception import ServiceError
from app.db import common_crud, crud
from app.db.orm import Experiment, File, Paradigm, ParadigmFile
from app.model import convert
from app.model.request import (
    DeleteModelRequest,
    GetModelsByPageParam,
    UpdateParadigmRequest,
    get_models_by_page,
)
from app.model.response import NoneResponse, Response, wrap_api_response
from app.model.schema import CreateParadigmRequest, ParadigmResponse

router = APIRouter(tags=["paradigm"])


@router.post("/api/createParadigm", description="创建实验范式", response_model=Response[int])
@wrap_api_response
def create_paradigm(
    request: CreateParadigmRequest, ctx: Context = Depends(researcher_context)
) -> int:
    database_error = ServiceError.database_fail("创建范式失败")

    deleted_experiments = common_crud.get_deleted_rows(ctx.db, Experiment, [request.experiment_id])
    if deleted_experiments is None:
        raise database_error
    elif len(deleted_experiments) > 0:
        raise ServiceError.not_found("未找到实验")
    deleted_files = common_crud.get_deleted_rows(ctx.db, File, request.images)
    if deleted_files is None:
        raise database_error
    elif len(deleted_files) > 0:
        raise ServiceError.not_found("未找到文件")

    paradigm_dict = {
        "experiment_id": request.experiment_id,
        "creator": ctx.user_id,
        "description": request.description,
    }
    paradigm_id = common_crud.insert_row(ctx.db, Paradigm, paradigm_dict, commit=False)
    if paradigm_id is None:
        raise database_error

    if len(request.images) > 0:
        files = [
            {"paradigm_id": paradigm_id, "file_id": file_id} for file_id in set(request.images)
        ]
        success = common_crud.bulk_insert_rows(ctx.db, ParadigmFile, files, commit=True)
        if not success:
            raise database_error

    return paradigm_id


@router.get("/api/getParadigmInfo", description="获取范式详情", response_model=Response[ParadigmResponse])
@wrap_api_response
def get_paradigm_info(
    paradigm_id: int = Query(description="范式ID", ge=0),
    ctx: Context = Depends(human_subject_context),
) -> ParadigmResponse:
    orm_paradigm = crud.get_paradigm_by_id(ctx.db, paradigm_id)
    if orm_paradigm is None:
        raise ServiceError.not_found("未找到范式")
    paradigm_response = convert.paradigm_orm_2_response(orm_paradigm)
    return paradigm_response


@router.get(
    "/api/getParadigmsByPage",
    description="分页获取范式详情",
    response_model=Response[list[ParadigmResponse]],
)
@wrap_api_response
def get_paradigms_by_page(
    experiment_id: int | None = Query(description="实验ID", default=None),
    page_param: GetModelsByPageParam = Depends(get_models_by_page),
    ctx: Context = Depends(human_subject_context),
) -> list[ParadigmResponse]:
    orm_paradigms = crud.search_paradigms_v2(ctx.db, experiment_id, page_param)
    paradigm_responses = convert.list_(convert.paradigm_orm_2_response, orm_paradigms)
    return paradigm_responses


@router.post("/api/updateParadigm", description="更新范式", response_model=NoneResponse)
@wrap_api_response
def update_paradigm(
    request: UpdateParadigmRequest, ctx: Context = Depends(researcher_context)
) -> None:
    database_error = ServiceError.database_fail("更新范式失败")

    update_dict = {
        field_name: field_value
        for field_name, field_value in request.dict(exclude={"id", "images"}).items()
        if field_value is not None
    }
    if len(update_dict) > 0:
        success = common_crud.update_row(
            ctx.db, Paradigm, request.id, update_dict, commit=(request.images is None)
        )
        if not success:
            raise database_error

    if request.images is not None:
        exist_paradigm_files = crud.list_paradigm_files(ctx.db, request.id)
        add_files = [
            {"paradigm_id": request.id, "file_id": file_id}
            for file_id in request.images
            if file_id not in exist_paradigm_files
        ]
        delete_files = [
            file_id for file_id in exist_paradigm_files if file_id not in request.images
        ]
        if len(add_files) > 0:
            success = common_crud.bulk_insert_rows(
                ctx.db, ParadigmFile, add_files, commit=(len(delete_files) < 1)
            )
            if not success:
                raise database_error
        if len(delete_files) > 0:
            success = common_crud.bulk_delete_rows(
                ctx.db,
                ParadigmFile,
                [ParadigmFile.paradigm_id == request.id, ParadigmFile.file_id.in_(delete_files)],
                commit=True,
            )
            if not success:
                raise database_error


@router.delete("/api/deleteParadigm", description="删除范式", response_model=NoneResponse)
@wrap_api_response
def delete_paradigm(
    request: DeleteModelRequest, ctx: Context = Depends(researcher_context)
) -> None:
    database_error = ServiceError.database_fail("删除范式失败")

    orm_files = crud.list_paradigm_file_infos(ctx.db, request.id)
    if orm_files:
        success = common_crud.bulk_update_rows_as_deleted(
            ctx.db, File, [file.id for file in orm_files], commit=False
        )
        if not success:
            raise database_error
        for file in orm_files:
            path = get_os_path(file.experiment_id, file.index, file.extension)
            delete_os_file(path)

    success = common_crud.update_row_as_deleted(ctx.db, Paradigm, request.id, commit=False)
    if not success:
        raise database_error
    success = common_crud.bulk_delete_rows(
        ctx.db, ParadigmFile, [ParadigmFile.paradigm_id == request.id], commit=True
    )
    if not success:
        raise database_error
