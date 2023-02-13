from fastapi import APIRouter, Depends, Query

from app.api import check_experiment_exists, check_user_exists
from app.common.context import AdministratorContext, HumanSubjectContext, ResearcherContext
from app.common.exception import ServiceError
from app.db import common_crud, crud
from app.db.orm import ExperimentHumanSubject, HumanSubject
from app.model import convert
from app.model.request import DeleteHumanSubjectRequest, UpdateExperimentHumanSubjectRequest
from app.model.response import NoneResponse, PagedData, Response, wrap_api_response
from app.model.schema import HumanSubjectCreate, HumanSubjectResponse, HumanSubjectSearch

router = APIRouter(tags=["human subject"])


@router.post("/api/createHumanSubject", description="创建人类被试者", response_model=Response[int])
@wrap_api_response
def create_human_subject(
    request: HumanSubjectCreate, ctx: AdministratorContext = Depends()
) -> None:
    check_user_exists(ctx.db, request.user_id)

    human_subject_dict = request.dict()
    human_subject_id = common_crud.insert_row(ctx.db, HumanSubject, human_subject_dict, commit=True)
    if human_subject_id is None:
        raise ServiceError.database_fail("创建人类被试者失败")


@router.delete("/api/deleteHumanSubject", description="删除人类被试者", response_model=NoneResponse)
@wrap_api_response
def delete_human_subject(
    request: DeleteHumanSubjectRequest, ctx: AdministratorContext = Depends()
) -> None:
    success = common_crud.update_row_as_deleted(
        ctx.db, HumanSubject, where=[HumanSubject.user_id == request.user_id], commit=True
    )
    if not success:
        raise ServiceError.database_fail("删除人类被试者失败")


@router.get(
    "/api/getHumanSubjectInfo",
    description="获取人类被试者详情",
    response_model=Response[HumanSubjectResponse],
)
@wrap_api_response
def get_human_subject_info(
    user_id: int = Query(description="用户ID", ge=0), ctx: HumanSubjectContext = Depends()
) -> HumanSubjectResponse:
    orm_human_subject = crud.get_human_subject(ctx.db, user_id)
    if orm_human_subject is None:
        raise ServiceError.not_found("未找到人类被试者")
    return convert.human_subject_orm_2_response(orm_human_subject)


@router.get(
    "/api/getHumanSubjectsByPage",
    description="分页获取人类被试者详情",
    response_model=Response[PagedData[HumanSubjectResponse]],
)
@wrap_api_response
def get_human_subjects_by_page(
    search: HumanSubjectSearch = Depends(), ctx: HumanSubjectContext = Depends()
) -> PagedData[HumanSubjectResponse]:
    total, human_subjects = crud.search_human_subjects(ctx.db, search)
    human_subjects_responses = convert.map_list(
        convert.human_subject_orm_2_response, human_subjects
    )
    return PagedData(total=total, items=human_subjects_responses)


@router.post(
    "/api/addHumanSubjectsInExperiment", description="向实验中添加人类被试者", response_model=NoneResponse
)
@wrap_api_response
def add_human_subjects_in_experiment(
    request: UpdateExperimentHumanSubjectRequest, ctx: ResearcherContext = Depends()
) -> None:
    check_experiment_exists(ctx.db, request.experiment_id)

    exist_human_subject_user_ids = set(
        crud.list_experiment_human_subjects(ctx.db, request.experiment_id)
    )
    add_experiment_human_subjects = [
        {"experiment_id": request.experiment_id, "user_id": user_id}
        for user_id in request.user_ids
        if user_id not in exist_human_subject_user_ids
    ]
    if not common_crud.bulk_insert_rows(
        ctx.db, ExperimentHumanSubject, add_experiment_human_subjects, commit=True
    ):
        raise ServiceError.database_fail("向实验中添加人类被试者失败")


@router.delete(
    "/api/deleteHumanSubjectsFromExperiment", description="从实验中删除人类被试者", response_model=NoneResponse
)
@wrap_api_response
def delete_human_subjects_from_experiment(
    request: UpdateExperimentHumanSubjectRequest, ctx: ResearcherContext = Depends()
) -> None:
    check_experiment_exists(ctx.db, request.experiment_id)

    success = common_crud.bulk_delete_rows(
        ctx.db,
        ExperimentHumanSubject,
        [
            ExperimentHumanSubject.experiment_id == request.experiment_id,
            ExperimentHumanSubject.user_id.in_(request.user_ids),
        ],
        commit=True,
    )
    if not success:
        raise ServiceError.database_fail("从实验中删除人类被试者失败")
