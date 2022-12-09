from fastapi import APIRouter, Depends, Query

from app.common.context import Context, human_subject_context, researcher_context
from app.common.time import convert_timezone_before_handle_request
from app.db import crud
from app.db.orm import Experiment, ExperimentAssistant
from app.model.request import (
    GetExperimentsByPageSortBy,
    GetExperimentsByPageSortOrder,
    GetModelsByPageParam,
    get_models_by_page,
)
from app.model.response import Response, wrap_api_response
from app.model.schema import (
    CreateExperimentRequest,
    ExperimentAssistantCreate,
    ExperimentCreate,
    ExperimentInDB,
    ExperimentResponse,
)

router = APIRouter(tags=["experiment"])


@router.post("/api/createExperiment", description="创建实验", response_model=Response[int])
@wrap_api_response
async def create_experiment(
    request: CreateExperimentRequest, ctx: Context = Depends(researcher_context)
) -> int:
    request = convert_timezone_before_handle_request(request)
    experiment_create = ExperimentCreate(**request.dict())
    experiment_id = crud.insert_model(ctx.db, Experiment, experiment_create)
    assistants = [
        ExperimentAssistantCreate(user_id=assistant_id, experiment_id=experiment_id)
        for assistant_id in request.assistants
    ]
    crud.bulk_insert_models(ctx.db, ExperimentAssistant, assistants)
    return experiment_id


@router.get(
    "/api/getExperimentInfo", description="获取实验详情", response_model=Response[ExperimentResponse]
)
@wrap_api_response
async def get_experiment_info(
    experiment_id: int = Query(description="实验ID"), ctx: Context = Depends(human_subject_context)
) -> ExperimentResponse:
    experiment = crud.get_model(ctx.db, Experiment, ExperimentInDB, experiment_id)
    assistants = crud.list_experiment_assistants(ctx.db, experiment_id)
    return ExperimentResponse(**experiment.dict(), assistants=assistants)


@router.get(
    "/api/getExperimentsByPage",
    description="获取实验列表",
    response_model=Response[list[ExperimentResponse]],
)
@wrap_api_response
async def get_experiments_by_page(
    search: str = Query(description="搜索任务名", default=""),
    sort_by: GetExperimentsByPageSortBy = Query(
        description="排序依据", default=GetExperimentsByPageSortBy.START_TIME
    ),
    sort_order: GetExperimentsByPageSortOrder = Query(
        description="排序顺序", default=GetExperimentsByPageSortOrder.DESC
    ),
    page_param: GetModelsByPageParam = Depends(get_models_by_page),
    ctx: Context = Depends(human_subject_context),
) -> list[ExperimentResponse]:
    experiments = crud.search_experiments(ctx.db, search, sort_by, sort_order, page_param)
    assistants_lists = crud.bulk_list_experiment_assistants(
        ctx.db, [experiment.id for experiment in experiments]
    )
    return [
        ExperimentResponse(**experiment.dict(), assistants=assistants)
        for experiment, assistants in zip(experiments, assistants_lists)
    ]
