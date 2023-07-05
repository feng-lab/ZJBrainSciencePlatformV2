import itertools

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

import app.db.crud.file as file_crud
import app.db.crud.paradigm as crud
from app.api import wrap_api_response
from app.api.file import delete_os_file
from app.common.config import config
from app.common.context import HumanSubjectContext, ResearcherContext
from app.common.exception import ServiceError
from app.common.localization import Entity
from app.db import common_crud
from app.db.orm import Experiment, Paradigm, StorageFile, VirtualFile
from app.model import convert
from app.model.request import DeleteModelRequest, UpdateParadigmRequest
from app.model.response import NoneResponse, Response
from app.model.schema import CreateParadigmRequest, PageParm, ParadigmResponse

router = APIRouter(tags=["paradigm"])


@router.post("/api/createParadigm", description="创建实验范式", response_model=Response[int])
@wrap_api_response
def create_paradigm(request: CreateParadigmRequest, ctx: ResearcherContext = Depends()) -> int:
    deleted_experiments = common_crud.get_deleted_rows(ctx.db, Experiment, [request.experiment_id])
    if deleted_experiments is None:
        raise ServiceError.database_fail()
    elif len(deleted_experiments) > 0:
        raise ServiceError.not_found(Entity.experiment)
    deleted_files = common_crud.get_deleted_rows(ctx.db, VirtualFile, request.images)
    if deleted_files is None:
        raise ServiceError.database_fail()
    elif len(deleted_files) > 0:
        raise ServiceError.not_found(Entity.file)

    paradigm_dict = {
        "experiment_id": request.experiment_id,
        "creator": ctx.user_id,
        "description": request.description,
    }
    paradigm_id = common_crud.insert_row(ctx.db, Paradigm, paradigm_dict, commit=True)
    if paradigm_id is None:
        raise ServiceError.database_fail()

    if len(request.images) > 0:
        success = common_crud.bulk_update_rows(
            ctx.db,
            VirtualFile,
            [VirtualFile.is_deleted == False, VirtualFile.id.in_(request.images)],
            {"paradigm_id": paradigm_id},
            commit=True,
        )
        if not success:
            raise ServiceError.database_fail()

    return paradigm_id


@router.get("/api/getParadigmInfo", description="获取范式详情", response_model=Response[ParadigmResponse])
@wrap_api_response
def get_paradigm_info(
    paradigm_id: int = Query(description="范式ID", ge=0), ctx: HumanSubjectContext = Depends()
) -> ParadigmResponse:
    orm_paradigm = crud.get_paradigm_by_id(ctx.db, paradigm_id)
    if orm_paradigm is None:
        raise ServiceError.not_found(Entity.paradigm)
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
    page_param: PageParm = Depends(),
    ctx: HumanSubjectContext = Depends(),
) -> list[ParadigmResponse]:
    orm_paradigms = crud.search_paradigms(ctx.db, experiment_id, page_param)
    paradigm_responses = convert.map_list(convert.paradigm_orm_2_response, orm_paradigms)
    return paradigm_responses


@router.post("/api/updateParadigm", description="更新范式", response_model=NoneResponse)
@wrap_api_response
def update_paradigm(request: UpdateParadigmRequest, ctx: ResearcherContext = Depends()) -> None:
    update_dict = request.dict(exclude={"id", "images"})
    if len(update_dict) > 0:
        success = common_crud.update_row(
            ctx.db, Paradigm, update_dict, id_=request.id, commit=False
        )
        if not success:
            raise ServiceError.database_fail()

    exist_paradigm_files = set(crud.list_paradigm_files(ctx.db, request.id))
    add_files = [file_id for file_id in request.images if file_id not in exist_paradigm_files]
    delete_files = [file_id for file_id in exist_paradigm_files if file_id not in request.images]
    add_file_success, delete_virtual_file_success, delete_storage_file_success = True, True, True
    if len(add_files) > 0:
        add_file_success = common_crud.bulk_update_rows(
            ctx.db,
            VirtualFile,
            [VirtualFile.is_deleted == False, VirtualFile.id.in_(add_files)],
            {"paradigm_id": request.id},
            commit=False,
        )
    if len(delete_files) > 0:
        for db_storage_path in file_crud.bulk_get_db_storage_paths(ctx.db, delete_files):
            delete_os_file(config.FILE_ROOT / db_storage_path)
        delete_virtual_file_success = common_crud.bulk_update_rows_as_deleted(
            ctx.db, VirtualFile, ids=delete_files, commit=False
        )
        delete_storage_file_success = common_crud.bulk_update_rows_as_deleted(
            ctx.db, StorageFile, where=[StorageFile.virtual_file_id.in_(delete_files)], commit=False
        )
    if add_file_success and delete_storage_file_success and delete_virtual_file_success:
        ctx.db.commit()
    else:
        ctx.db.rollback()
        raise ServiceError.database_fail()


@router.delete("/api/deleteParadigm", description="删除范式", response_model=NoneResponse)
@wrap_api_response
def delete_paradigm(request: DeleteModelRequest, ctx: ResearcherContext = Depends()) -> None:
    if not delete_paradigm_files(ctx.db, request.id):
        raise ServiceError.database_fail()
    if not common_crud.update_row_as_deleted(ctx.db, Paradigm, id_=request.id, commit=True):
        raise ServiceError.database_fail()


def delete_paradigm_files(db: Session, paradigm_id: int) -> bool:
    virtual_file_infos = crud.get_paradigm_file_infos(db, paradigm_id)
    if len(virtual_file_infos) < 1:
        return True

    virtual_file_ids = [virtual_file.id for virtual_file in virtual_file_infos]
    if not common_crud.bulk_update_rows_as_deleted(
        db, VirtualFile, ids=virtual_file_ids, commit=False
    ):
        return False
    storage_files: list[StorageFile] = list(
        itertools.chain.from_iterable(
            virtual_file.storage_files for virtual_file in virtual_file_infos
        )
    )
    storage_file_ids = [storage_file.id for storage_file in storage_files]
    if not common_crud.bulk_update_rows_as_deleted(
        db, StorageFile, ids=storage_file_ids, commit=False
    ):
        return False

    for storage_file in storage_files:
        delete_os_file(config.FILE_ROOT / storage_file.storage_path)

    return True
