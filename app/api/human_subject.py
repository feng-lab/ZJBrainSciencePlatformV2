from fastapi import APIRouter, Depends, Query

from app.api import check_experiment_exists, check_human_subject_exists, wrap_api_response
from app.common.context import HumanSubjectContext, ResearcherContext
from app.common.exception import ServiceError
from app.common.localization import Entity
from app.common.user_auth import AccessLevel, hash_password
from app.db import common_crud
from app.db.crud import human_subject as crud
from app.db.orm import ExperimentHumanSubject, HumanSubject, User
from app.model import convert
from app.model.request import DeleteHumanSubjectRequest, UpdateExperimentHumanSubjectRequest
from app.model.response import CreateHumanSubjectResponse, NoneResponse, Page, Response
from app.model.schema import HumanSubjectCreate, HumanSubjectResponse, HumanSubjectSearch, HumanSubjectUpdate

router = APIRouter(tags=["human subject"])


@router.post("/api/createHumanSubject", description="创建人类被试者", response_model=Response[CreateHumanSubjectResponse])
@wrap_api_response
def create_human_subject(request: HumanSubjectCreate, ctx: ResearcherContext = Depends()) -> CreateHumanSubjectResponse:
    next_index = crud.get_next_human_subject_index(ctx.db)
    username = f"HS{next_index:06}"
    password = f"{username}#brain#{username}"
    user_dict = {
        "username": username,
        "staff_id": username,
        "access_level": AccessLevel.HUMAN_SUBJECT.value,
        "hashed_password": hash_password(password),
    }
    user_id = common_crud.insert_row(ctx.db, User, user_dict, commit=True)
    if user_id is None:
        raise ServiceError.database_fail()

    human_subject_dict = request.dict() | {"user_id": user_id}
    human_subject_id = common_crud.insert_row(ctx.db, HumanSubject, human_subject_dict, commit=True)
    if human_subject_id is None:
        raise ServiceError.database_fail()

    return CreateHumanSubjectResponse(user_id=user_id, username=username, staff_id=username, password=password)


@router.delete("/api/deleteHumanSubjects", description="批量删除人类被试者", response_model=NoneResponse)
@wrap_api_response
def delete_human_subjects(request: DeleteHumanSubjectRequest, ctx: ResearcherContext = Depends()) -> None:
    success = common_crud.bulk_update_rows_as_deleted(
        ctx.db, HumanSubject, where=[HumanSubject.user_id.in_(request.user_ids)], commit=False
    )
    if not success:
        raise ServiceError.database_fail()
    success = common_crud.bulk_update_rows_as_deleted(ctx.db, User, where=[User.id.in_(request.user_ids)], commit=True)
    if not success:
        raise ServiceError.database_fail()


@router.get("/api/getHumanSubjectInfo", description="获取人类被试者详情", response_model=Response[HumanSubjectResponse])
@wrap_api_response
def get_human_subject_info(
    user_id: int = Query(description="用户ID", ge=0), ctx: HumanSubjectContext = Depends()
) -> HumanSubjectResponse:
    orm_human_subject = crud.get_human_subject(ctx.db, user_id)
    if orm_human_subject is None:
        raise ServiceError.not_found(Entity.human_subject)
    return convert.human_subject_orm_2_response(orm_human_subject)


@router.get(
    "/api/getHumanSubjectsByPage", description="分页获取人类被试者详情", response_model=Response[Page[HumanSubjectResponse]]
)
@wrap_api_response
def get_human_subjects_by_page(
    search: HumanSubjectSearch = Depends(), ctx: HumanSubjectContext = Depends()
) -> Page[HumanSubjectResponse]:
    total, human_subjects = crud.search_human_subjects(ctx.db, search)
    human_subjects_responses = convert.map_list(convert.human_subject_orm_2_response, human_subjects)
    return Page(total=total, items=human_subjects_responses)


@router.post("/api/updateHumanSubject", description="更新人类被试者", response_model=NoneResponse)
@wrap_api_response
def update_human_subject(update: HumanSubjectUpdate, ctx: ResearcherContext = Depends()) -> None:
    check_human_subject_exists(ctx.db, update.user_id)

    update_dict = update.dict(exclude={"user_id"})
    success = common_crud.update_row(
        ctx.db, HumanSubject, update_dict, where=[HumanSubject.user_id == update.user_id], commit=True
    )
    if not success:
        raise ServiceError.database_fail()


@router.post("/api/addHumanSubjectsInExperiment", description="向实验中添加人类被试者", response_model=NoneResponse)
@wrap_api_response
def add_human_subjects_in_experiment(
    request: UpdateExperimentHumanSubjectRequest, ctx: ResearcherContext = Depends()
) -> None:
    check_experiment_exists(ctx.db, request.experiment_id)

    exist_human_subject_user_ids = set(crud.list_experiment_human_subjects(ctx.db, request.experiment_id))
    add_experiment_human_subjects = [
        {"experiment_id": request.experiment_id, "user_id": user_id}
        for user_id in request.user_ids
        if user_id not in exist_human_subject_user_ids
    ]
    if not common_crud.bulk_insert_rows(ctx.db, ExperimentHumanSubject, add_experiment_human_subjects, commit=True):
        raise ServiceError.database_fail()


@router.delete("/api/deleteHumanSubjectsFromExperiment", description="从实验中删除人类被试者", response_model=NoneResponse)
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
        raise ServiceError.database_fail()
