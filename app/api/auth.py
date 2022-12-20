from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.common.config import config
from app.common.context import Context, all_user_context
from app.common.time import utc_now
from app.common.user_auth import (
    TOKEN_TYPE,
    create_access_token,
    raise_unauthorized_exception,
    verify_password,
)
from app.db import crud, get_db_session
from app.db.orm import User
from app.model.response import LoginResponse, NoneResponse, wrap_api_response

router = APIRouter(tags=["auth"])


@router.post("/api/login", description="用户登录，获取AccessToken", response_model=LoginResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db_session)):
    # 验证用户名与密码是否匹配
    user_id = verify_password(db, form.username, form.password)
    if user_id is None:
        raise_unauthorized_exception(username=form.username)

    # 创建登录凭证
    access_token = create_access_token(user_id, config.ACCESS_TOKEN_EXPIRE_MINUTES)

    # 更新最近登录时间
    crud.update_model(db, User, user_id, last_login_time=utc_now())

    return LoginResponse(access_token=access_token, token_type=TOKEN_TYPE)


@router.post("/api/logout", description="用户登出", response_model=NoneResponse)
@wrap_api_response
def logout(ctx: Context = Depends(all_user_context)) -> None:
    crud.update_model(ctx.db, User, ctx.user_id, last_logout_time=utc_now())
