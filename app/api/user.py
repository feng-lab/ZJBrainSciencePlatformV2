from fastapi import APIRouter, Depends, HTTPException, Query
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND

from app.api.auth import (
    AccessLevel,
    get_current_user,
    get_current_user_as_administrator,
    hash_password,
    verify_password,
)
from app.db import crud
from app.model.db_model import User
from app.model.request import (
    CreateUserRequest,
    DeleteUserRequest,
    GetModelsByPageParam,
    UpdatePasswordRequest,
    UpdateUserAccessLevelRequest,
    get_models_by_page,
)
from app.model.response import ListUserData, NoneResponse, Response, UserInfo, wrap_api_response
from app.util import convert_models

router = APIRouter()

ROOT_USERNAME = "root"
ROOT_PASSWORD = "?L09G$7g5*j@.q*4go4d"


@router.post("/api/createUser", description="创建用户", response_model=Response[int])
@wrap_api_response
async def create_user(
    request: CreateUserRequest, _user: User = Depends(get_current_user_as_administrator())
) -> int:
    # 用户名唯一，幂等处理
    user = await crud.get_user_by_username(request.username)
    if user is None:
        # 数据库不能保存密码明文，只能保存密码哈希值
        hashed_password = hash_password(request.password)
        user = User(**request.dict(exclude={"password"}), hashed_password=hashed_password)
        user = await crud.create_model(user)
    return user.id


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


@router.get("/api/getCurrentUserInfo", description="获取当前用户信息", response_model=Response[UserInfo])
@wrap_api_response
async def get_current_user_info(user: User = Depends(get_current_user)) -> UserInfo:
    return UserInfo(**user.dict())


@router.get("/api/getUserInfo", description="获取用户信息", response_model=Response[UserInfo])
@wrap_api_response
async def get_user_info(
    _admin: User = Depends(get_current_user_as_administrator()),
    user_id: int = Query(alias="id", description="用户ID", ge=0),
) -> UserInfo:
    user = await crud.get_model_by_id(User, user_id)
    if user is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="用户不存在")
    return UserInfo(**user.dict())


@router.get("/api/getUsersByPage", description="获取用户列表", response_model=Response[ListUserData])
@wrap_api_response
async def get_users_by_page(
    _user: User = Depends(get_current_user_as_administrator()),
    username: str | None = Query(description="用户名，模糊查询", max_length=255, default=None),
    staff_id: str | None = Query(description="员工号，模糊查询", max_length=255, default=None),
    access_level: int | None = Query(description="权限级别", ge=0, default=None),
    page_param: GetModelsByPageParam = Depends(get_models_by_page),
) -> ListUserData:
    total_count, users = await crud.search_users(
        username,
        staff_id,
        access_level,
        page_param.offset,
        page_param.limit,
        page_param.include_deleted,
    )
    return ListUserData(total=total_count, items=convert_models(users, UserInfo))


@router.post("/api/updateUserAccessLevel", description="修改用户权限", response_model=NoneResponse)
@wrap_api_response
async def update_user_access_level(
    request: UpdateUserAccessLevelRequest,
    _user: User = Depends(get_current_user_as_administrator()),
) -> None:
    update_user = await crud.get_model_by_id(User, request.id)
    if update_user is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="用户不存在")
    await crud.update_model(update_user, access_level=request.access_level)


@router.post("/api/updatePassword", description="用户修改密码", response_model=NoneResponse)
@wrap_api_response
async def update_password(
    request: UpdatePasswordRequest, user: User = Depends(get_current_user)
) -> None:
    db_user = await verify_password(user.username, request.old_password)
    if db_user is None or db_user.id != user.id or db_user.username != user.username:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="原密码错误")
    hashed_new_password = hash_password(request.new_password)
    await crud.update_model(db_user, hashed_password=hashed_new_password)


@router.delete("/api/deleteUser", description="删除用户", response_model=NoneResponse)
@wrap_api_response
async def delete_user(
    request: DeleteUserRequest, _user: User = Depends(get_current_user_as_administrator())
) -> None:
    user = await crud.get_model_by_id(User, request.id)
    await crud.update_model(user, is_deleted=True)
