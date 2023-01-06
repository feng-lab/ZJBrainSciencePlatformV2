from fastapi import APIRouter, Depends, HTTPException, Query
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from app.common.context import Context, human_subject_context, researcher_context
from app.db import crud
from app.db.orm import Experiment, Paradigm, ParadigmFile
from app.model.request import (
    DeleteModelRequest,
    GetModelsByPageParam,
    UpdateParadigmRequest,
    get_models_by_page,
)
from app.model.response import NoneResponse, Response, wrap_api_response
from app.model.schema import (
    CreateParadigmRequest,
    ParadigmCreate,
    ParadigmFileCreate,
    ParadigmResponse,
)

router = APIRouter(tags=["paradigm"])


@router.post("/api/createParadigm", description="创建实验范式", response_model=Response[int])
@wrap_api_response
def create_paradigm(
    request: CreateParadigmRequest, ctx: Context = Depends(researcher_context)
) -> int:
    if not crud.exists_model(ctx.db, Experiment, request.experiment_id):
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="experiment not exists")

    paradigm_create = ParadigmCreate(
        experiment_id=request.experiment_id, creator=ctx.user_id, description=request.description
    )
    paradigm_id = crud.insert_model(ctx.db, Paradigm, paradigm_create)
    paradigm_files = [
        ParadigmFileCreate(paradigm_id=paradigm_id, file_id=file_id) for file_id in request.images
    ]
    crud.bulk_insert_models(ctx.db, ParadigmFile, paradigm_files)
    return paradigm_id


@router.get("/api/getParadigmInfo", description="获取范式详情", response_model=Response[ParadigmResponse])
@wrap_api_response
def get_paradigm_info(
    paradigm_id: int = Query(description="范式ID", ge=0),
    ctx: Context = Depends(human_subject_context),
) -> ParadigmResponse:
    paradigm = crud.get_paradigm_by_id(ctx.db, paradigm_id)
    if paradigm is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="paradigm not found")
    paradigm.images = crud.list_paradigm_files(ctx.db, paradigm_id)
    return paradigm


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
    if not crud.exists_model(ctx.db, Experiment, experiment_id):
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="experiment not exists")

    paradigms = crud.search_paradigms(ctx.db, experiment_id, page_param)
    paradigm_files_list = crud.bulk_list_paradigm_files(
        ctx.db, [paradigm.id for paradigm in paradigms]
    )
    for paradigm, paradigm_files in zip(paradigms, paradigm_files_list):
        paradigm.images = paradigm_files
    return paradigms


@router.post("/api/updateParadigm", description="更新范式", response_model=NoneResponse)
@wrap_api_response
def update_paradigm(
    request: UpdateParadigmRequest, ctx: Context = Depends(researcher_context)
) -> None:
    update_dict = {
        field_name: field_value
        for field_name, field_value in request.dict(exclude={"id", "images"}).items()
        if field_value is not None
    }
    if len(update_dict) > 0:
        crud.update_model(ctx.db, Paradigm, request.id, **update_dict)

    if request.images is not None:
        exist_paradigm_files = crud.list_paradigm_files(ctx.db, request.id)
        add_files = [
            ParadigmFileCreate(paradigm_id=request.id, file_id=file_id)
            for file_id in request.images
            if file_id not in exist_paradigm_files
        ]
        if len(add_files) > 0:
            crud.bulk_insert_models(ctx.db, ParadigmFile, add_files)

        delete_files = [file_id for file_id in exist_paradigm_files if file_id not in request.images]
        if len(delete_files) > 0:
            crud.bulk_update_models_as_deleted(
                ctx.db,
                ParadigmFile,
                ParadigmFile.paradigm_id == request.id,
                ParadigmFile.file_id.in_(delete_files),
            )


@router.delete("/api/deleteParadigm", description="删除范式", response_model=NoneResponse)
@wrap_api_response
def delete_paradigm(
    request: DeleteModelRequest, ctx: Context = Depends(researcher_context)
) -> None:
    crud.update_model_as_deleted(ctx.db, Paradigm, request.id)
    crud.bulk_update_models_as_deleted(ctx.db, ParadigmFile, ParadigmFile.id == request.id)
