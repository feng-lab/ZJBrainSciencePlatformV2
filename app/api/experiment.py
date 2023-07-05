from fastapi import APIRouter, Depends, Query

from app.api import wrap_api_response
from app.common.context import HumanSubjectContext, ResearcherContext
from app.common.exception import ServiceError
from app.common.localization import Entity
from app.db import common_crud
from app.db.crud import experiment as crud
from app.db.orm import Experiment, ExperimentAssistant, ExperimentTag
from app.model import convert
from app.model.request import (
    DeleteModelRequest,
    UpdateExperimentAssistantsRequest,
    UpdateExperimentRequest,
)
from app.model.response import NoneResponse, Response
from app.model.schema import (
    CreateExperimentRequest,
    ExperimentResponse,
    ExperimentSearch,
    ExperimentSimpleResponse,
    UserInfo,
)

router = APIRouter(tags=["experiment"])


@router.post("/api/createExperiment", description="创建实验", response_model=Response[int])
@wrap_api_response
def create_experiment(request: CreateExperimentRequest, ctx: ResearcherContext = Depends()) -> int:
    experiment_id = common_crud.insert_row(
        ctx.db, Experiment, request.dict(exclude={"assistants", "tags"}), commit=False
    )
    if experiment_id is None:
        raise ServiceError.database_fail()

    if len(request.assistants) > 0:
        assistants = [
            {"user_id": assistant_id, "experiment_id": experiment_id}
            for assistant_id in set(request.assistants)
        ]
        all_inserted = common_crud.bulk_insert_rows(
            ctx.db, ExperimentAssistant, assistants, commit=False
        )
        if not all_inserted:
            raise ServiceError.database_fail()

    if len(request.tags) > 0:
        tags = [{"experiment_id": experiment_id, "tag": tag} for tag in set(request.tags)]
        all_inserted = common_crud.bulk_insert_rows(ctx.db, ExperimentTag, tags, commit=False)
        if not all_inserted:
            raise ServiceError.database_fail()

    ctx.db.commit()
    return experiment_id


@router.get(
    "/api/getExperimentInfo", description="获取实验详情", response_model=Response[ExperimentResponse]
)
@wrap_api_response
def get_experiment_info(
    experiment_id: int = Query(description="实验ID"), ctx: HumanSubjectContext = Depends()
) -> ExperimentResponse:
    orm_experiment = crud.get_experiment_by_id(ctx.db, experiment_id)
    if orm_experiment is None:
        raise ServiceError.not_found(Entity.experiment)

    experiment = convert.experiment_orm_2_response(orm_experiment)
    return experiment


@router.get(
    "/api/getExperimentsByPage",
    description="获取实验列表",
    response_model=Response[list[ExperimentSimpleResponse]],
)
@wrap_api_response
def get_experiments_by_page(
    search: ExperimentSearch = Depends(), ctx: HumanSubjectContext = Depends()
) -> list[ExperimentSimpleResponse]:
    orm_experiments = crud.search_experiments(ctx.db, search)
    experiments = convert.map_list(convert.experiment_orm_2_simple_response, orm_experiments)
    return experiments


@router.get(
    "/api/getExperimentAssistants", description="获取实验助手列表", response_model=Response[list[UserInfo]]
)
@wrap_api_response
def get_experiment_assistants(
    experiment_id: int = Query(description="实验ID"), ctx: HumanSubjectContext = Depends()
) -> list[UserInfo]:
    orm_users = crud.list_experiment_assistants(ctx.db, experiment_id)
    user_infos = convert.map_list(UserInfo.from_orm, orm_users)
    return user_infos


@router.post("/api/updateExperiment", description="更新实验", response_model=NoneResponse)
@wrap_api_response
def update_experiment(request: UpdateExperimentRequest, ctx: ResearcherContext = Depends()):
    update_dict = {
        field_name: field_value
        for field_name, field_value in request.dict(exclude={"id", "tags"}).items()
        if field_value is not None
    }
    success = common_crud.update_row(ctx.db, Experiment, update_dict, id_=request.id, commit=False)
    if not success:
        raise ServiceError.database_fail()

    if request.tags is not None and len(request.tags) > 0:
        success = crud.update_experiment_tags(ctx.db, request.id, set(request.tags))
        if not success:
            raise ServiceError.database_fail()

    ctx.db.commit()


@router.delete("/api/deleteExperiment", description="删除实验", response_model=NoneResponse)
@wrap_api_response
def delete_experiment(request: DeleteModelRequest, ctx: ResearcherContext = Depends()) -> None:
    delete_experiment_success = common_crud.update_row_as_deleted(
        ctx.db, Experiment, id_=request.id, commit=False
    )
    delete_tags_success = common_crud.bulk_delete_rows(
        ctx.db, ExperimentTag, [ExperimentTag.experiment_id == request.id], commit=False
    )
    if delete_experiment_success and delete_tags_success:
        ctx.db.commit()


@router.post("/api/addExperimentAssistants", description="添加实验助手", response_model=NoneResponse)
@wrap_api_response
def add_experiment_assistants(
    request: UpdateExperimentAssistantsRequest, ctx: ResearcherContext = Depends()
) -> None:
    exist_assistants = set(
        crud.search_experiment_assistants(ctx.db, request.experiment_id, request.assistant_ids)
    )
    assistants = [
        {"user_id": assistant_id, "experiment_id": request.experiment_id}
        for assistant_id in request.assistant_ids
        if assistant_id not in exist_assistants
    ]
    if len(assistants) > 0:
        success = common_crud.bulk_insert_rows(ctx.db, ExperimentAssistant, assistants, commit=True)
        if not success:
            raise ServiceError.database_fail()


@router.delete("/api/deleteExperimentAssistants", description="删除实验助手", response_model=NoneResponse)
@wrap_api_response
def delete_experiment_assistants(
    request: UpdateExperimentAssistantsRequest, ctx: ResearcherContext = Depends()
) -> None:
    success = common_crud.bulk_delete_rows(
        ctx.db,
        ExperimentAssistant,
        [
            ExperimentAssistant.experiment_id == request.experiment_id,
            ExperimentAssistant.user_id.in_(request.assistant_ids),
        ],
        commit=True,
    )
    if not success:
        raise ServiceError.database_fail()
