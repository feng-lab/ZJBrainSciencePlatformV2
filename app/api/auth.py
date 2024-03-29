from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import decrypt_password, wrap_api_response
from app.common.config import config
from app.common.context import AllUserContext
from app.common.exception import ServiceError
from app.common.user_auth import TOKEN_TYPE, create_access_token, raise_unauthorized_exception, verify_password
from app.common.util import now
from app.db import common_crud, get_db_session
from app.db.orm import User
from app.model.response import LoginResponse, NoneResponse

router = APIRouter(tags=["auth"])


@router.post("/api/login", description="用户登录，获取AccessToken", response_model=LoginResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db_session)):
    # 验证用户名与密码是否匹配
    password = decrypt_password(form.password)
    user_id = verify_password(db, form.username, password)
    if user_id is None:
        raise_unauthorized_exception(staff_id=form.username)

    # 创建登录凭证
    access_token = create_access_token(user_id, config.ACCESS_TOKEN_EXPIRE_MINUTES)

    # 更新最近登录时间
    success = common_crud.update_row(db, User, {"last_login_time": now()}, id_=user_id, commit=True)
    if not success:
        raise ServiceError.database_fail()

    return LoginResponse(access_token=access_token, token_type=TOKEN_TYPE)


@router.post("/api/logout", description="用户登出", response_model=NoneResponse)
@wrap_api_response
def logout(ctx: AllUserContext = Depends()) -> None:
    success = common_crud.update_row(ctx.db, User, {"last_logout_time": now()}, id_=ctx.user_id, commit=True)
    if not success:
        raise ServiceError.database_fail()
