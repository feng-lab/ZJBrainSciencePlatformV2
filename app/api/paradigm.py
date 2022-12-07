from fastapi import APIRouter, Depends, HTTPException, Query
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from app.api.auth import get_current_user_as_human_subject, get_current_user_as_researcher
from app.db import crud
from app.model.db_model import Experiment, Paradigm, ParadigmFile, User
from app.model.request import CreateParadigmRequest
from app.model.response import ParadigmInfo, Response, wrap_api_response

router = APIRouter()


@router.post("/api/createParadigm", description="创建实验范式", response_model=Response[int])
@wrap_api_response
async def create_paradigm(
    request: CreateParadigmRequest, user: User = Depends(get_current_user_as_researcher())
) -> int:
    if not await crud.model_exists(Experiment, request.experiment_id):
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="experiment not exists")

    paradigm = Paradigm(
        experiment_id=request.experiment_id, creator=user.id, description=request.description
    )
    paradigm = await crud.create_model(paradigm)
    paradigm_files = [
        ParadigmFile(paradigm_id=paradigm.id, file_id=file_id) for file_id in request.images
    ]
    await crud.bulk_create_models(paradigm_files)
    return paradigm.id


@router.get("/api/getParadigmInfo", description="获取范式详情", response_model=Response[ParadigmInfo])
@wrap_api_response
async def get_paradigm_info(
    paradigm_id: int = Query(description="范式ID", ge=0),
    _user: User = Depends(get_current_user_as_human_subject()),
) -> ParadigmInfo:
    paradigm = await crud.get_model_by_id(Paradigm, paradigm_id)
    if paradigm is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="paradigm not found")
    paradigm_files = await crud.search_models(ParadigmFile, paradigm_id=paradigm.id)
    images = [paradigm_file.file_id for paradigm_file in paradigm_files]
    paradigm_info = ParadigmInfo(**paradigm.dict(), images=images)
    return paradigm_info
