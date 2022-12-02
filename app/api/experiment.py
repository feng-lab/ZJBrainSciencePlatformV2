from fastapi import APIRouter, Depends

from app.api.auth import get_current_user_as_researcher
from app.db import crud
from app.model.db_model import User, Experiment
from app.model.request import CreateExperimentRequest
from app.model.response import CreateExperimentResponse
from app.utils import request_add_timezone

router = APIRouter()


@router.post(
    "/api/createExperiment", description="创建实验", response_model=CreateExperimentResponse
)
async def create_experiment(
    request: CreateExperimentRequest,
    _user: User = Depends(get_current_user_as_researcher()),
):
    request = request_add_timezone(request)
    experiment = Experiment(**request.dict())
    experiment = await crud.create_experiment(experiment)
    return CreateExperimentResponse(data=experiment.id)
