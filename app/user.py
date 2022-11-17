from datetime import datetime, timedelta
from typing import NoReturn

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, ExpiredSignatureError, JWTError
from loguru import logger
from passlib.context import CryptContext
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED

from app import crud
from app.config import get_config
from app.models import User
from app.requests import CreateUserRequest
from app.responses import LoginResponse, CODE_SUCCESS, Response
from app.schemas import AccessTokenData

router = APIRouter()

crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

TOKEN_TYPE = "bearer"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")
SECRET_KEY = "4ebcc6180a124d9f3a618e48d97c32a6d99085d5cfdf25a6368d1e0ff3943bd0"
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    hashed_password = crypt_context.hash(password)
    return hashed_password


def verify_password(password: str, hashed_password: str) -> bool:
    is_valid_password = crypt_context.verify(password, hashed_password)
    return is_valid_password


async def authenticate_user(username: str, password: str) -> User | None:
    user = await User.objects.get_or_none(username=username, is_deleted=False)
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(user_id: int, expire_minutes: int) -> str:
    sub = str(user_id)
    expire_at = datetime.utcnow() + timedelta(minutes=expire_minutes)
    token_data = AccessTokenData(sub=sub, exp=expire_at)
    token = jwt.encode(token_data.dict(), SECRET_KEY, algorithm=ALGORITHM)
    return token


async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> User:
    """获取当前用户ID"""
    try:
        # 从token中解码AccessTokenData
        payload_dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = AccessTokenData(**payload_dict)
        user_id = int(token_data.sub)

        # 验证用户存在
        user = await User.objects.get_or_none(id=user_id, is_deleted=False)
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


def raise_unauthorized_exception(data: dict) -> NoReturn:
    logger.error(f"unauthorized user, {data=}")
    raise HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="wrong username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/api/createUser", description="创建用户", response_model=Response)
async def create_user(request: CreateUserRequest):
    # 用户名唯一
    user = await User.objects.get_or_none(username=request.username, is_deleted=False)
    if user is not None:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="User already exists"
        )

    # 数据库不能保存密码明文，只能保存密码哈希值
    hashed_password = hash_password(request.password)
    await crud.create_user(request, hashed_password)

    return Response(code=CODE_SUCCESS, message="Create user success")


@router.post(
    "/api/login", response_model=LoginResponse, description="用户登录，获取AccessToken"
)
async def login(form: OAuth2PasswordRequestForm = Depends()):
    username = form.username

    # 验证用户名与密码是否匹配
    user = await authenticate_user(username, form.password)
    if user is None:
        raise_unauthorized_exception({"username": username})

    # 创建登录凭证
    access_token = create_access_token(
        user.id, get_config().ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # 更新最近登录时间
    utcnow = datetime.utcnow()
    await user.update(last_login_time=utcnow, gmt_modified=utcnow)

    return LoginResponse(access_token=access_token, token_type=TOKEN_TYPE)


@router.post("/api/logout", response_model=Response, description="用户登出")
async def logout(user: User = Depends(get_current_user_id)):
    utcnow = datetime.utcnow()
    await user.update(last_logout_time=utcnow, gmt_modified=utcnow)

    return Response(code=CODE_SUCCESS, message="logout success")
