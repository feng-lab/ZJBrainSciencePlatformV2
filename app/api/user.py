from fastapi import APIRouter, Depends, HTTPException, Query
from starlette.status import HTTP_401_UNAUTHORIZED

from app.common.context import AdministratorContext, AllUserContext
from app.common.exception import ServiceError
from app.common.user_auth import hash_password, verify_password
from app.db import cache, common_crud, crud
from app.db.orm import User
from app.model.request import (
    DeleteModelRequest,
    UpdatePasswordRequest,
    UpdateUserAccessLevelRequest,
)
from app.model.response import NoneResponse, PagedData, Response, wrap_api_response
from app.model.schema import CreateUserRequest, PageParm, UserResponse

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
    user_dict = request.dict(exclude={"password"}) | {
        "hashed_password": hash_password(request.password)
    }
    user_id = common_crud.insert_row(ctx.db, User, user_dict, commit=True)
    if user_id is None:
        raise ServiceError.database_fail("创建用户失败")
    return user_id


@router.get(
    "/api/getCurrentUserInfo", description="获取当前用户信息", response_model=Response[UserResponse]
)
@wrap_api_response
def get_current_user_info(ctx: AllUserContext = Depends()) -> UserResponse:
    orm_user = common_crud.get_row_by_id(ctx.db, User, ctx.user_id)
    user = UserResponse.from_orm(orm_user)
    return user


@router.get("/api/getUserInfo", description="获取用户信息", response_model=Response[UserResponse])
@wrap_api_response
def get_user_info(
    user_id: int = Query(alias="id", description="用户ID", ge=0),
    ctx: AdministratorContext = Depends(),
) -> UserResponse:
    orm_user = common_crud.get_row_by_id(ctx.db, User, user_id)
    if orm_user is None:
        raise ServiceError.not_found("未找到用户")
    user = UserResponse.from_orm(orm_user)
    return user


@router.get(
    "/api/getUsersByPage", description="获取用户列表", response_model=Response[PagedData[UserResponse]]
)
@wrap_api_response
def get_users_by_page(
    username: str | None = Query(description="用户名，模糊查询", max_length=255, default=None),
    staff_id: str | None = Query(description="员工号，模糊查询", max_length=255, default=None),
    access_level: int | None = Query(description="权限级别", ge=0, default=None),
    page_param: PageParm = Depends(),
    ctx: AdministratorContext = Depends(),
) -> PagedData[UserResponse]:
    paged_data = crud.search_users(ctx.db, username, staff_id, access_level, page_param)
    return paged_data


@router.post("/api/updateUserAccessLevel", description="修改用户权限", response_model=NoneResponse)
@wrap_api_response
def update_user_access_level(
    request: UpdateUserAccessLevelRequest, ctx: AdministratorContext = Depends()
) -> None:
    user_exists = common_crud.exists_row(ctx.db, User, id_=request.id)
    if not user_exists:
        raise ServiceError.invalid_request("用户不存在")

    success = common_crud.update_row(
        ctx.db, User, {"access_level": request.access_level}, id=request.id, commit=True
    )
    if success:
        cache.invalidate_user_access_level(ctx.cache, request.id)
    else:
        raise ServiceError.database_fail("修改用户权限失败")


@router.post("/api/updatePassword", description="用户修改密码", response_model=NoneResponse)
@wrap_api_response
def update_password(request: UpdatePasswordRequest, ctx: AllUserContext = Depends()) -> None:
    staff_id = crud.get_user_staff_id(ctx.db, ctx.user_id)
    user_id = verify_password(ctx.db, staff_id, request.old_password)
    if user_id is None or user_id != ctx.user_id:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="原密码错误")
    hashed_new_password = hash_password(request.new_password)
    success = common_crud.update_row(
        ctx.db, User, {"hashed_password": hashed_new_password}, id=user_id, commit=True
    )
    if not success:
        raise ServiceError.database_fail("用户修改密码失败")


@router.delete("/api/deleteUser", description="删除用户", response_model=NoneResponse)
@wrap_api_response
def delete_user(request: DeleteModelRequest, ctx: AdministratorContext = Depends()) -> None:
    success = common_crud.update_row_as_deleted(ctx.db, User, id=request.id, commit=True)
    if not success:
        raise ServiceError.database_fail("删除用户失败")
