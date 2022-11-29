from datetime import timedelta
from enum import Enum
from typing import NoReturn

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, ExpiredSignatureError, JWTError
from loguru import logger
from passlib.context import CryptContext
from starlette.status import HTTP_401_UNAUTHORIZED

from app.config import config
from app.db import crud
from app.model.db_model import User
from app.model.response import LoginResponse, Response
from app.model.schema import AccessTokenData
from app.utils import utc_now

router = APIRouter()

crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
TOKEN_TYPE = "bearer"
SECRET_KEY = "4ebcc6180a124d9f3a618e48d97c32a6d99085d5cfdf25a6368d1e0ff3943bd0"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")


class AccessLevel(Enum):
    MINIMUM = 0
    HUMAN_SUBJECT = 10
    RESEARCHER = 100
    ADMINISTRATOR = 1000


def get_current_user_with_level(api_access_level: int):
    async def wrapper(user: User = Depends(get_current_user)) -> User:
        if user.access_level < api_access_level:
            logger.error(f"unauthorized api invocation, {user.id=}")
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="用户没有调用本API的权限"
            )
        return user

    return wrapper


def get_current_user_as_human_subject():
    return get_current_user_with_level(AccessLevel.HUMAN_SUBJECT.value)


def get_current_user_as_researcher():
    return get_current_user_with_level(AccessLevel.RESEARCHER.value)


def get_current_user_as_administrator():
    return get_current_user_with_level(AccessLevel.ADMINISTRATOR.value)


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


def create_access_token(user_id: int, expire_minutes: int) -> str:
    sub = str(user_id)
    expire_at = utc_now() + timedelta(minutes=expire_minutes)
    token_data = AccessTokenData(sub=sub, exp=expire_at)
    token = jwt.encode(token_data.dict(), SECRET_KEY, algorithm=ALGORITHM)
    return token


def hash_password(password: str) -> str:
    return crypt_context.hash(password)


def raise_unauthorized_exception(data: dict) -> NoReturn:
    logger.error(f"unauthorized user, {data=}")
    raise HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="wrong username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


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
        user.id, config.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # 更新最近登录时间
    await crud.update_user(user, last_login_time=utc_now())

    return LoginResponse(access_token=access_token, token_type=TOKEN_TYPE)


@router.post("/api/logout", description="用户登出", response_model=Response)
async def logout(user: User = Depends(get_current_user)):
    await crud.update_user(user, last_logout_time=utc_now())
    return Response()
