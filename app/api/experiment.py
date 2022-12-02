from fastapi import APIRouter, Depends, Query

from app.api.auth import (
    get_current_user_as_researcher,
    get_current_user_as_human_subject,
)
from app.db import crud
from app.model.db_model import User, Experiment
from app.model.request import CreateExperimentRequest
from app.model.response import CreateExperimentResponse, GetExperimentInfoResponse
from app.timezone_util import convert_timezone_before_handle_request
from app.utils import custom_json_response

router = APIRouter()


@router.post(
    "/api/createExperiment", description="创建实验", response_model=CreateExperimentResponse
)
async def create_experiment(
    request: CreateExperimentRequest,
    _user: User = Depends(get_current_user_as_researcher()),
):
    request = convert_timezone_before_handle_request(request)
    experiment = Experiment(**request.dict())
    experiment = await crud.create_model(experiment)
    return CreateExperimentResponse(data=experiment.id)


@router.get(
    "/api/getExperimentInfo",
    description="获取实验详情",
    response_model=GetExperimentInfoResponse,
)
@custom_json_response
async def get_experiment_info(
    _user: User = Depends(get_current_user_as_human_subject()),
    experiment_id: int = Query(description="实验ID"),
):
    experiment = await crud.get_model_by_id(Experiment, experiment_id)
    return experiment
