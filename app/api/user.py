from fastapi import APIRouter, Depends, Query

import app.db.crud.user as crud
from app.api import check_user_exists, wrap_api_response
from app.common.context import AdministratorContext, AllUserContext, ResearcherContext
from app.common.exception import ServiceError
from app.common.localization import Entity
from app.common.user_auth import hash_password, verify_password
from app.db import cache, common_crud
from app.db.orm import User
from app.model import convert
from app.model.request import DeleteModelRequest, UpdatePasswordRequest, UpdateUserAccessLevelRequest
from app.model.response import NoneResponse, Page, Response
from app.model.schema import CreateUserRequest, UserResponse, UserSearch

router = APIRouter(tags=["user"])

ROOT_USERNAME = "root"
ROOT_PASSWORD = "?L09G$7g5*j@.q*4go4d"


@router.post("/api/createUser", description="创建用户", response_model=Response[int])
@wrap_api_response
def create_user(request: CreateUserRequest, ctx: AdministratorContext = Depends()) -> int:
    # staff_id唯一，幂等处理
    exists_user = common_crud.get_row(ctx.db, User, User.staff_id == request.staff_id)
    if exists_user is not None:
        return exists_user.id

    # 数据库不能保存密码明文，只能保存密码哈希值
    user_dict = request.dict(exclude={"password"}) | {"hashed_password": hash_password(request.password)}
    user_id = common_crud.insert_row(ctx.db, User, user_dict, commit=True)
    if user_id is None:
        raise ServiceError.database_fail()
    return user_id


@router.get("/api/getCurrentUserInfo", description="获取当前用户信息", response_model=Response[UserResponse])
@wrap_api_response
def get_current_user_info(ctx: AllUserContext = Depends()) -> UserResponse:
    orm_user = common_crud.get_row_by_id(ctx.db, User, ctx.user_id)
    user = UserResponse.from_orm(orm_user)
    return user


@router.get("/api/getUserInfo", description="获取用户信息", response_model=Response[UserResponse])
@wrap_api_response
def get_user_info(
    user_id: int = Query(alias="id", description="用户ID", ge=0), ctx: AdministratorContext = Depends()
) -> UserResponse:
    orm_user = common_crud.get_row_by_id(ctx.db, User, user_id)
    if orm_user is None:
        raise ServiceError.not_found(Entity.user)
    user = UserResponse.from_orm(orm_user)
    return user


@router.get("/api/getUsersByPage", description="获取用户列表", response_model=Response[Page[UserResponse]])
@wrap_api_response
def get_users_by_page(search: UserSearch = Depends(), ctx: ResearcherContext = Depends()) -> Page[UserResponse]:
    total, orm_users = crud.search_users(ctx.db, search)
    user_responses = convert.map_list(convert.user_orm_2_response, orm_users)
    return Page(total=total, items=user_responses)


@router.post("/api/updateUserAccessLevel", description="修改用户权限", response_model=NoneResponse)
@wrap_api_response
def update_user_access_level(request: UpdateUserAccessLevelRequest, ctx: AdministratorContext = Depends()) -> None:
    check_user_exists(ctx.db, request.id)

    success = common_crud.update_row(ctx.db, User, {"access_level": request.access_level}, id_=request.id, commit=True)
    if success:
        cache.invalidate_user_access_level(ctx.cache, request.id)
    else:
        raise ServiceError.database_fail()


@router.post("/api/updatePassword", description="用户修改密码", response_model=NoneResponse)
@wrap_api_response
def update_password(request: UpdatePasswordRequest, ctx: AllUserContext = Depends()) -> None:
    staff_id = crud.get_user_staff_id(ctx.db, ctx.user_id)
    user_id = verify_password(ctx.db, staff_id, request.old_password)
    if user_id is None or user_id != ctx.user_id:
        raise ServiceError.wrong_password()
    hashed_new_password = hash_password(request.new_password)
    success = common_crud.update_row(ctx.db, User, {"hashed_password": hashed_new_password}, id_=user_id, commit=True)
    if not success:
        raise ServiceError.database_fail()


@router.delete("/api/deleteUser", description="删除用户", response_model=NoneResponse)
@wrap_api_response
def delete_user(request: DeleteModelRequest, ctx: AdministratorContext = Depends()) -> None:
    success = common_crud.update_row_as_deleted(ctx.db, User, id_=request.id, commit=True)
    if not success:
        raise ServiceError.database_fail()
