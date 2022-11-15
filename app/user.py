from fastapi import APIRouter, HTTPException
from objprint import op
from passlib.context import CryptContext
from starlette.status import HTTP_400_BAD_REQUEST

from app import crud
from app.requests import LoginRequest, CreateUserRequest
from app.responses import LoginResponse, CODE_SUCCESS

router = APIRouter()

crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    hashed_password = crypt_context.hash(password)
    return hashed_password


@router.post("/api/createUser", description="创建用户")
async def create_user(request: CreateUserRequest):
    op(request)
    if await crud.get_user(request.username) is not None:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="User already exists"
        )

    hashed_password = hash_password(request.password)
    await crud.create_user(request, hashed_password)


@router.post("/api/login", response_model=LoginResponse, description="用户提交登录表单，进行登录验证")
def login(request: LoginRequest):
    op(request)
    return LoginResponse(code=CODE_SUCCESS)
