from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from app.api.auth import get_current_user_as_researcher
from app.db import crud
from app.model.db_model import Experiment, Paradigm, ParadigmFile, User
from app.model.request import CreateParadigmRequest
from app.model.response import Response, wrap_api_response

router = APIRouter()


@router.post("/api/createParadigm", description="创建实验范式", response_model=Response[int])
@wrap_api_response
async def create_paradigm(
    request: CreateParadigmRequest, user: User = Depends(get_current_user_as_researcher())
):
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
