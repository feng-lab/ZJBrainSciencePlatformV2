from fastapi import APIRouter, Depends, Query, HTTPException
from starlette.status import HTTP_404_NOT_FOUND

from app.api.auth import (
    get_current_user,
    hash_password,
    get_current_user_as_administrator,
    AccessLevel,
)
from app.db import crud
from app.model.db_model import User
from app.model.request import CreateUserRequest, UpdateUserAccessLevelRequest
from app.model.response import (
    Response,
    ListUsersResponse,
    GetCurrentUserInfoResponse,
    CreateUserResponse,
)
from app.utils import custom_json_response

router = APIRouter()

ROOT_USERNAME = "root"
ROOT_PASSWORD = "?L09G$7g5*j@.q*4go4d"


@router.post("/api/createUser", description="创建用户", response_model=CreateUserResponse)
async def create_user(
    request: CreateUserRequest,
    _user: User = Depends(get_current_user_as_administrator()),
):
    # 用户名唯一，幂等处理
    user = await crud.get_user_by_username(request.username)
    if user is None:
        # 数据库不能保存密码明文，只能保存密码哈希值
        hashed_password = hash_password(request.password)
        user = User(
            **request.dict(exclude={"password"}), hashed_password=hashed_password
        )
        user = await crud.create_user(user)

    return CreateUserResponse(data=user.id)


async def create_root_user() -> None:
    root_user_dict = {
        "username": ROOT_USERNAME,
        "hashed_password": hash_password(ROOT_PASSWORD),
        "staff_id": ROOT_USERNAME,
        "access_level": AccessLevel.ADMINISTRATOR.value,
    }
    root_user = await crud.get_user_by_username(ROOT_USERNAME)
    if root_user is not None:
        await crud.update_user(root_user, **root_user_dict)
    else:
        await crud.create_user(User(**root_user_dict))


@router.get(
    "/api/getCurrentUserInfo",
    description="获取当前用户信息",
    response_model=GetCurrentUserInfoResponse,
)
@custom_json_response
async def get_current_user_info(user: User = Depends(get_current_user)):
    return GetCurrentUserInfoResponse(data=user)


@router.get(
    "/api/getUsersByPage", description="获取用户列表", response_model=ListUsersResponse
)
@custom_json_response
async def get_users_by_page(
    _user: User = Depends(get_current_user_as_administrator()),
    offset: int = Query(description="列表起始位置", default=0),
    limit: int = Query(description="列表大小", default=10),
    include_deleted: bool = Query(description="是否包括已删除项", default=False),
):
    users = await crud.list_users(offset, limit, include_deleted)
    return ListUsersResponse(data=users)


@router.post(
    "/api/updateUserAccessLevel", description="修改用户权限", response_model=Response
)
async def update_user_access_level(
    request: UpdateUserAccessLevelRequest,
    _user: User = Depends(get_current_user_as_administrator()),
):
    update_user = await crud.get_user_by_id(request.user_id)
    if update_user is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="用户不存在")
    await crud.update_user(update_user, access_level=request.access_level)
    return Response()


@router.delete("/api/deleteUser", description="删除用户", response_model=Response)
async def delete_user(
    _user: User = Depends(get_current_user_as_administrator()),
    user_id: int = Query(description="用户ID"),
):
    await crud.update_user(user_id, is_deleted=True)
    return Response()
