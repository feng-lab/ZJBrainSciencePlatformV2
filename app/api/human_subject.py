from fastapi import APIRouter, Depends, Query

from app.common.context import HumanSubjectContext, ResearcherContext
from app.common.exception import ServiceError
from app.db import common_crud, crud
from app.db.orm import HumanSubject, User, Experiment, ExperimentHumanSubject
from app.model import convert
from app.model.request import UpdateExperimentHumanSubjectRequest
from app.model.response import PagedData, Response, wrap_api_response, NoneResponse
from app.model.schema import HumanSubjectCreate, HumanSubjectResponse, HumanSubjectSearch

router = APIRouter(tags=["human subject"])


@router.post("/api/createHumanSubject", description="创建人类被试者", response_model=Response[int])
@wrap_api_response
def create_human_subject(request: HumanSubjectCreate, ctx: ResearcherContext = Depends()) -> None:
    database_error = ServiceError.database_fail("创建人类被试者失败")

    # 检查user_id
    user_is_valid = common_crud.check_row_valid(ctx.db, User, request.user_id)
    if user_is_valid is None:
        raise database_error
    elif not user_is_valid:
        raise ServiceError.not_found("用户不存在")

    human_subject_dict = request.dict()
    human_subject_id = common_crud.insert_row(ctx.db, HumanSubject, human_subject_dict, commit=True)
    if human_subject_id is None:
        raise database_error


@router.get(
    "/api/getHumanSubjectInfo",
    description="获取人类被试者详情",
    response_model=Response[HumanSubjectResponse],
)
@wrap_api_response
def get_human_subject_info(
    user_id: int = Query(description="用户ID", ge=0), ctx: HumanSubjectContext = Depends()
) -> HumanSubjectResponse:
    orm_human_subject = common_crud.get_row(ctx.db, HumanSubject, HumanSubject.user_id == user_id)
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
    "/api/addHumanSubjectsInExperiment", description="添加实验人类被试者", response_model=NoneResponse
)
@wrap_api_response
def add_human_subjects_in_experiment(
    request: UpdateExperimentHumanSubjectRequest, ctx: ResearcherContext = Depends()
) -> None:
    database_error = ServiceError.database_fail("添加实验人类被试者失败")

    experiment_exists = common_crud.check_row_valid(ctx.db, Experiment, request.experiment_id)
    if experiment_exists is None:
        raise database_error
    elif not experiment_exists:
        raise ServiceError.not_found("实验不存在")

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
        raise database_error
