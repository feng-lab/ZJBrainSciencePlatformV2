from fastapi import APIRouter, Depends, Query

from app.api.auth import get_current_user_as_human_subject, get_current_user_as_researcher
from app.db import crud
from app.model.db_model import Experiment, ExperimentAssistant, User
from app.model.request import (
    CreateExperimentRequest,
    GetExperimentsByPageSortBy,
    GetExperimentsByPageSortOrder,
    GetModelsByPageParam,
    get_models_by_page,
)
from app.model.response import ExperimentInfo, Response, wrap_api_response
from app.time import convert_timezone_before_handle_request
from app.util import convert_models

router = APIRouter(tags=["experiment"])


@router.post("/api/createExperiment", description="创建实验", response_model=Response[int])
@wrap_api_response
async def create_experiment(
    request: CreateExperimentRequest, _user: User = Depends(get_current_user_as_researcher())
) -> int:
    request = convert_timezone_before_handle_request(request)
    experiment = Experiment(**request.dict())
    experiment = await crud.create_model(experiment)
    assistants = [
        ExperimentAssistant(user_id=assistant_id, experiment_id=experiment.id)
        for assistant_id in request.assistants
    ]
    await crud.bulk_create_models(assistants)
    return experiment.id


@router.get("/api/getExperimentInfo", description="获取实验详情", response_model=Response[ExperimentInfo])
@wrap_api_response
async def get_experiment_info(
    _user: User = Depends(get_current_user_as_human_subject()),
    experiment_id: int = Query(description="实验ID"),
) -> ExperimentInfo:
    experiment = await crud.get_model_by_id(Experiment, experiment_id)
    assistants = await crud.search_models(ExperimentAssistant, experiment_id=experiment_id)
    experiment.assistants = [assistant.user_id for assistant in assistants]
    return ExperimentInfo(**experiment.dict())


@router.get(
    "/api/getExperimentsByPage", description="获取实验列表", response_model=Response[list[ExperimentInfo]]
)
@wrap_api_response
async def get_experiments_by_page(
    _user: User = Depends(get_current_user_as_human_subject()),
    search: str = Query(description="搜索任务名", default=""),
    sort_by: GetExperimentsByPageSortBy = Query(
        description="排序依据", default=GetExperimentsByPageSortBy.START_TIME
    ),
    sort_order: GetExperimentsByPageSortOrder = Query(
        description="排序顺序", default=GetExperimentsByPageSortOrder.DESC
    ),
    page_param: GetModelsByPageParam = Depends(get_models_by_page),
) -> list[ExperimentInfo]:
    experiments = await crud.search_experiments(
        search, sort_by, sort_order, page_param.offset, page_param.limit, page_param.include_deleted
    )
    assistant_lists = await crud.bulk_search_models_by_key(
        ExperimentAssistant, [experiment.id for experiment in experiments], "experiment_id"
    )
    for experiment, assistants in zip(experiments, assistant_lists):
        experiment.assistants = [assistant.id for assistant in assistants]
    return convert_models(experiments, ExperimentInfo)
