from fastapi import APIRouter, Depends, Query

from app.api.file import delete_os_file, get_os_path
from app.common.context import Context, human_subject_context, researcher_context
from app.common.exception import ServiceError
from app.db import common_crud, crud
from app.db.orm import Experiment, File, Paradigm
from app.model import convert
from app.model.request import DeleteModelRequest, GetModelsByPageParam, UpdateParadigmRequest
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
    paradigm_id = common_crud.insert_row(ctx.db, Paradigm, paradigm_dict, commit=True)
    if paradigm_id is None:
        raise database_error

    if len(request.images) > 0:
        success = common_crud.bulk_update_rows(
            ctx.db,
            File,
            [File.is_deleted == False, File.id.in_(request.images)],
            {"paradigm_id": paradigm_id},
            commit=True,
        )
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
    experiment_id: int = Query(description="实验ID", default=0),
    page_param: GetModelsByPageParam = Depends(),
    ctx: Context = Depends(human_subject_context),
) -> list[ParadigmResponse]:
    orm_paradigms = crud.search_paradigms(ctx.db, experiment_id, page_param)
    paradigm_responses = convert.map_list(convert.paradigm_orm_2_response, orm_paradigms)
    return paradigm_responses


@router.post("/api/updateParadigm", description="更新范式", response_model=NoneResponse)
@wrap_api_response
def update_paradigm(
    request: UpdateParadigmRequest, ctx: Context = Depends(researcher_context)
) -> None:
    database_error = ServiceError.database_fail("更新范式失败")

    update_dict = request.dict(exclude={"id", "images"})
    if len(update_dict) > 0:
        success = common_crud.update_row(ctx.db, Paradigm, request.id, update_dict, commit=False)
        if not success:
            raise database_error

    exist_paradigm_files = set(crud.list_paradigm_files(ctx.db, request.id))
    add_files = [file_id for file_id in request.images if file_id not in exist_paradigm_files]
    delete_files = [file_id for file_id in exist_paradigm_files if file_id not in request.images]
    if len(add_files) > 0:
        success = common_crud.bulk_update_rows(
            ctx.db,
            File,
            [File.is_deleted == False, File.id.in_(add_files)],
            {"paradigm_id": request.id},
            commit=(len(delete_files) < 1),
        )
        if not success:
            raise database_error
    if len(delete_files) > 0:
        success = common_crud.bulk_update_rows_as_deleted(ctx.db, File, delete_files, commit=True)
        if not success:
            raise database_error
    if len(add_files) < 1 and len(delete_files) < 1:
        ctx.db.commit()


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

    success = common_crud.update_row_as_deleted(ctx.db, Paradigm, request.id, commit=True)
    if not success:
        raise database_error
