from fastapi import APIRouter, Depends

from app.common.context import Context, researcher_context
from app.common.exception import ServiceError
from app.db import common_crud
from app.db.orm import HumanSubject, User
from app.model.response import Response, wrap_api_response
from app.model.schema import CreateHumanSubjectRequest

router = APIRouter(tags=["human subject"])


@router.post("/api/createHumanSubject", description="创建人类被试者", response_model=Response[int])
@wrap_api_response
def create_human_subject(
    request: CreateHumanSubjectRequest, ctx: Context = Depends(researcher_context)
) -> int:
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
    return human_subject_id
