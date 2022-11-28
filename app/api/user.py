from datetime import timedelta
from typing import NoReturn

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, ExpiredSignatureError, JWTError
from loguru import logger
from passlib.context import CryptContext
from starlette.status import HTTP_401_UNAUTHORIZED

from app.config import get_config
from app.db import crud
from app.model.db_model import User, utc_now
from app.model.request import CreateUserRequest
from app.model.response import (
    LoginResponse,
    Response,
    ListUsersResponse,
    GetCurrentUserInfoResponse,
    CreateUserResponse,
)
from app.model.schema import AccessTokenData

router = APIRouter()

crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

TOKEN_TYPE = "bearer"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")
SECRET_KEY = "4ebcc6180a124d9f3a618e48d97c32a6d99085d5cfdf25a6368d1e0ff3943bd0"
ALGORITHM = "HS256"

ROOT_USERNAME = "root"
ROOT_PASSWORD = "?L09G$7g5*j@.q*4go4d"


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """获取当前用户"""
    try:
        # 从token中解码AccessTokenData
        payload_dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = AccessTokenData(**payload_dict)
        user_id = int(token_data.sub)

        # 验证用户存在
        user = await crud.get_user_by_id(user_id)
        if user is None:
            raise_unauthorized_exception({"user_id": user_id})
        return user
    except ExpiredSignatureError as e:
        # token过期
        token_payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"verify_signature": False},
        )
        logger.info(f"token expired, {token_payload=}")
        raise e
    except JWTError:
        logger.exception(f"invalid token")
        raise_unauthorized_exception({"token": token})


async def get_current_super_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_super_user:
        logger.error(f"user is not super user, {user.id=}")
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="user is not super user"
        )
    return user


def create_access_token(user_id: int, expire_minutes: int) -> str:
    sub = str(user_id)
    expire_at = utc_now() + timedelta(minutes=expire_minutes)
    token_data = AccessTokenData(sub=sub, exp=expire_at)
    token = jwt.encode(token_data.dict(), SECRET_KEY, algorithm=ALGORITHM)
    return token


def raise_unauthorized_exception(data: dict) -> NoReturn:
    logger.error(f"unauthorized user, {data=}")
    raise HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="wrong username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/api/createUser", description="创建用户", response_model=CreateUserResponse)
async def create_user(request: CreateUserRequest):
    # 用户名唯一，幂等处理
    user = await crud.get_user_by_username(request.username)
    if user is None:
        # 数据库不能保存密码明文，只能保存密码哈希值
        hashed_password = crypt_context.hash(request.password)
        user = User(
            **request.dict(exclude={"password"}), hashed_password=hashed_password
        )
        user = await crud.create_user(user)

    return CreateUserResponse(data=user.id)


async def create_root_user() -> None:
    root_user_dict = {
        "username": ROOT_USERNAME,
        "hashed_password": crypt_context.hash(ROOT_PASSWORD),
        "staff_id": ROOT_USERNAME,
        "account_type": ROOT_USERNAME,
        "is_super_user": True,
    }
    root_user = await crud.get_user_by_username(ROOT_USERNAME)
    if root_user is not None:
        await crud.update_user(root_user, **root_user_dict)
    else:
        await crud.create_user(User(**root_user_dict))


@router.post(
    "/api/login", description="用户登录，获取AccessToken", response_model=LoginResponse
)
async def login(form: OAuth2PasswordRequestForm = Depends()):
    username = form.username

    # 验证用户名与密码是否匹配
    user = await crud.get_user_by_username(username)
    if user is None or not crypt_context.verify(form.password, user.hashed_password):
        raise_unauthorized_exception({"username": username})

    # 创建登录凭证
    access_token = create_access_token(
        user.id, get_config().ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # 更新最近登录时间
    await crud.update_user(user, last_login_time=utc_now())

    return LoginResponse(access_token=access_token, token_type=TOKEN_TYPE)


@router.post("/api/logout", description="用户登出", response_model=Response)
async def logout(user: User = Depends(get_current_user)):
    await crud.update_user(user, last_logout_time=utc_now())
    return Response()


@router.get(
    "/api/getCurrentUserInfo",
    description="获取当前用户信息",
    response_model=GetCurrentUserInfoResponse,
)
async def get_current_user_info(user: User = Depends(get_current_user)):
    return GetCurrentUserInfoResponse(data=user)


@router.get(
    "/api/getUsersByPage", description="获取用户列表", response_model=ListUsersResponse
)
async def get_users_by_page(
    _user: User = Depends(get_current_super_user),
    offset: int = Query(description="列表起始位置", default=0),
    limit: int = Query(description="列表大小", default=10),
    include_deleted: bool = Query(description="是否包括已删除项", default=False),
):
    users = await crud.list_users(offset, limit, include_deleted)
    return ListUsersResponse(data=users)


@router.delete("/api/deleteUser", description="删除用户", response_model=Response)
async def delete_user(
    _user: User = Depends(get_current_super_user),
    user_id: int = Query(description="用户ID"),
):
    await crud.update_user(user_id, is_deleted=True)
    return Response()
