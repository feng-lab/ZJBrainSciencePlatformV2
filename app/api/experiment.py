from fastapi import APIRouter, Depends, HTTPException, Query
from starlette.status import HTTP_404_NOT_FOUND

from app.common.context import Context, human_subject_context, researcher_context
from app.common.exception import ServiceError
from app.db import common_crud, crud
from app.db.orm import Experiment, ExperimentAssistant
from app.model.request import (
    DeleteModelRequest,
    GetExperimentsByPageSortBy,
    GetExperimentsByPageSortOrder,
    GetModelsByPageParam,
    UpdateExperimentAssistantsRequest,
    UpdateExperimentRequest,
    get_models_by_page,
)
from app.model.response import NoneResponse, Response, wrap_api_response
from app.model.schema import (
    CreateExperimentRequest,
    ExperimentAssistantCreate,
    ExperimentResponse,
    UserIdNameStaffId,
)

router = APIRouter(tags=["experiment"])


@router.post("/api/createExperiment", description="创建实验", response_model=Response[int])
@wrap_api_response
def create_experiment(
    request: CreateExperimentRequest, ctx: Context = Depends(researcher_context)
) -> int:
    database_error = ServiceError.database_fail("创建实验失败")

    experiment_id = common_crud.insert_table(
        ctx.db, Experiment, request.dict(exclude={"assistants"}), commit=False
    )
    if experiment_id is None:
        raise database_error

    if len(request.assistants) > 0:
        assistants = [
            {"user_id": assistant_id, "experiment_id": experiment_id}
            for assistant_id in set(request.assistants)
        ]
        all_inserted = common_crud.bulk_insert_table(
            ctx.db, ExperimentAssistant, assistants, commit=True
        )
        if not all_inserted:
            raise database_error

    return experiment_id


@router.get(
    "/api/getExperimentInfo", description="获取实验详情", response_model=Response[ExperimentResponse]
)
@wrap_api_response
def get_experiment_info(
    experiment_id: int = Query(description="实验ID"), ctx: Context = Depends(human_subject_context)
) -> ExperimentResponse:
    experiment = crud.get_experiment_by_id(ctx.db, experiment_id)
    if experiment is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="experiment not exists")
    experiment.assistants = crud.list_experiment_assistants(ctx.db, experiment_id)
    return experiment


@router.get(
    "/api/getExperimentsByPage",
    description="获取实验列表",
    response_model=Response[list[ExperimentResponse]],
)
@wrap_api_response
def get_experiments_by_page(
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
    if len(experiments) < 1:
        return []
    assistants_lists = crud.bulk_list_experiment_assistants(
        ctx.db, [experiment.id for experiment in experiments]
    )
    for experiment, assistants in zip(experiments, assistants_lists):
        experiment.assistants = assistants
    return experiments


@router.get(
    "/api/getExperimentAssistants",
    description="获取实验助手列表",
    response_model=Response[list[UserIdNameStaffId]],
)
@wrap_api_response
def get_experiment_assistants(
    experiment_id: int = Query(description="实验ID"), ctx: Context = Depends(human_subject_context)
) -> list[UserIdNameStaffId]:
    return crud.list_experiment_assistants(ctx.db, experiment_id)


@router.post("/api/updateExperiment", description="更新实验", response_model=NoneResponse)
@wrap_api_response
def update_experiment(request: UpdateExperimentRequest, ctx: Context = Depends(researcher_context)):
    update_dict = {
        field_name: field_value
        for field_name, field_value in request.dict(exclude={"id"}).items()
        if field_value is not None
    }
    crud.update_model(ctx.db, Experiment, request.id, **update_dict)


@router.delete("/api/deleteExperiment", description="删除实验", response_model=NoneResponse)
@wrap_api_response
def delete_experiment(
    request: DeleteModelRequest, ctx: Context = Depends(researcher_context)
) -> None:
    crud.update_model(ctx.db, Experiment, request.id, is_deleted=True)


@router.post("/api/addExperimentAssistants", description="添加实验助手", response_model=NoneResponse)
@wrap_api_response
def add_experiment_assistants(
    request: UpdateExperimentAssistantsRequest, ctx: Context = Depends(researcher_context)
) -> None:
    exist_assistants = set(
        crud.search_experiment_assistants(ctx.db, request.experiment_id, request.assistant_ids)
    )
    assistants = [
        ExperimentAssistantCreate(user_id=assistant_id, experiment_id=request.experiment_id)
        for assistant_id in request.assistant_ids
        if assistant_id not in exist_assistants
    ]
    crud.bulk_insert_models(ctx.db, ExperimentAssistant, assistants)


@router.delete("/api/deleteExperimentAssistants", description="删除实验助手", response_model=NoneResponse)
@wrap_api_response
def delete_experiment_assistants(
    request: UpdateExperimentAssistantsRequest, ctx: Context = Depends(researcher_context)
) -> None:
    crud.bulk_update_models_as_deleted(
        ctx.db,
        ExperimentAssistant,
        ExperimentAssistant.experiment_id == request.experiment_id,
        ExperimentAssistant.user_id.in_(request.assistant_ids),
    )
