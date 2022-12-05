from fastapi import APIRouter, Depends, Query, HTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_401_UNAUTHORIZED

from app.api.auth import (
    get_current_user,
    hash_password,
    get_current_user_as_administrator,
    AccessLevel,
    verify_password,
)
from app.db import crud
from app.model.db_model import User
from app.model.request import CreateUserRequest, UpdateUserAccessLevelRequest, UpdatePasswordRequest
from app.model.response import Response, ListUsersResponse, GetUserInfoResponse, CreateUserResponse
from app.utils import custom_json_response

router = APIRouter()

ROOT_USERNAME = "root"
ROOT_PASSWORD = "?L09G$7g5*j@.q*4go4d"


@router.post("/api/createUser", description="创建用户", response_model=CreateUserResponse)
async def create_user(request: CreateUserRequest, _user: User = Depends(get_current_user_as_administrator())):
    # 用户名唯一，幂等处理
    user = await crud.get_user_by_username(request.username)
    if user is None:
        # 数据库不能保存密码明文，只能保存密码哈希值
        hashed_password = hash_password(request.password)
        user = User(**request.dict(exclude={"password"}), hashed_password=hashed_password)
        user = await crud.create_model(user)

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
        await crud.update_model(root_user, **root_user_dict)
    else:
        await crud.create_model(User(**root_user_dict))


@router.get("/api/getCurrentUserInfo", description="获取当前用户信息", response_model=GetUserInfoResponse)
@custom_json_response
async def get_current_user_info(user: User = Depends(get_current_user)):
    return GetUserInfoResponse(data=user)


@router.get("/api/getUserInfo", description="获取用户信息", response_model=GetUserInfoResponse)
@custom_json_response
async def get_user_info(
    _admin: User = Depends(get_current_user_as_administrator()),
    user_id: int = Query(alias="id", description="用户ID", ge=0),
):
    user = await crud.get_model_by_id(User, user_id)
    if user is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="用户不存在")
    return GetUserInfoResponse(data=user)


@router.get("/api/getUsersByPage", description="获取用户列表", response_model=ListUsersResponse)
@custom_json_response
async def get_users_by_page(
    _user: User = Depends(get_current_user_as_administrator()),
    username: str | None = Query(description="用户名，模糊查询", max_length=255, default=None),
    staff_id: str | None = Query(description="员工号，模糊查询", max_length=255, default=None),
    access_level: int | None = Query(description="权限级别", ge=0, default=None),
    offset: int = Query(description="列表起始位置", default=0),
    limit: int = Query(description="列表大小", default=10),
    include_deleted: bool = Query(description="是否包括已删除项", default=False),
):
    total_count, users = await crud.search_users(username, staff_id, access_level, offset, limit, include_deleted)
    return ListUsersResponse(data=ListUsersResponse.Data(total=total_count, items=users))


@router.post("/api/updateUserAccessLevel", description="修改用户权限", response_model=Response)
async def update_user_access_level(
    request: UpdateUserAccessLevelRequest, _user: User = Depends(get_current_user_as_administrator())
):
    update_user = await crud.get_model_by_id(User, request.id)
    if update_user is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="用户不存在")
    await crud.update_model(update_user, access_level=request.access_level)
    return Response()


@router.post("/api/updatePassword", description="用户修改密码", response_model=Response)
async def update_password(request: UpdatePasswordRequest, user: User = Depends(get_current_user)):
    db_user = await verify_password(user.username, request.old_password)
    if db_user is None or db_user.id != user.id or db_user.username != user.username:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="原密码错误")
    hashed_new_password = hash_password(request.new_password)
    await crud.update_model(db_user, hashed_password=hashed_new_password)
    return Response()


@router.delete("/api/deleteUser", description="删除用户", response_model=Response)
async def delete_user(
    _user: User = Depends(get_current_user_as_administrator()), user_id: int = Query(alias="id", description="用户ID")
):
    user = await crud.get_model_by_id(User, user_id)
    await crud.update_model(user, is_deleted=True)
    return Response()
