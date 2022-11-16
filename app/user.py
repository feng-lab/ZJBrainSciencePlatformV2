from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
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
    user = await crud.get_user(username)
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(username: str, expire_minutes: int) -> str:
    expire_at = datetime.utcnow() + timedelta(minutes=expire_minutes)
    token_data = AccessTokenData(username=username, expire_at=expire_at.timestamp())
    token = jwt.encode(token_data.dict(), SECRET_KEY, algorithm=ALGORITHM)
    return token


@router.post("/api/createUser", description="创建用户", response_model=Response)
async def create_user(request: CreateUserRequest):
    if await crud.get_user(request.username) is not None:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="User already exists"
        )

    hashed_password = hash_password(request.password)
    await crud.create_user(request, hashed_password)
    return Response(code=CODE_SUCCESS, message="Create user success")


@router.post(
    "/api/login", response_model=LoginResponse, description="用户登录，获取AccessToken"
)
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form.username, form.password)
    if user is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Wrong username or password"
        )

    access_token = create_access_token(
        form.username, get_config().ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return LoginResponse(
        code=CODE_SUCCESS,
        message="login success",
        data=LoginResponse.Token(access_token=access_token, token_type=TOKEN_TYPE),
    )
