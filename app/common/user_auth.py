import logging
from datetime import timedelta
from enum import IntEnum
from typing import NoReturn

from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext
from redis import Redis
from sqlalchemy.orm import Session

import app.db.crud.user as crud_user
from app.common.exception import ServiceError
from app.common.util import utc_now
from app.db.cache import get_user_access_level
from app.model.response import AccessTokenData

logger = logging.getLogger(__name__)

crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
TOKEN_TYPE = "bearer"
SECRET_KEY = "4ebcc6180a124d9f3a618e48d97c32a6d99085d5cfdf25a6368d1e0ff3943bd0"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login", auto_error=False)


class AccessLevel(IntEnum):
    MINIMUM = 0
    HUMAN_SUBJECT = 10
    RESEARCHER = 100
    ADMINISTRATOR = 1000


def create_access_token(user_id: int, expire_minutes: int) -> str:
    sub = str(user_id)
    expire_at = utc_now() + timedelta(minutes=expire_minutes)
    token_data = AccessTokenData(sub=sub, exp=expire_at)
    token = jwt.encode(token_data.dict(), SECRET_KEY, algorithm=ALGORITHM)
    return token


def hash_password(password: str) -> str:
    return crypt_context.hash(password)


def raise_unauthorized_exception(**data) -> NoReturn:
    logger.error(f"unauthorized user, {data=}")
    raise ServiceError.wrong_password()


def verify_current_user(db: Session, cache: Redis, token: str, api_access_level: int) -> int:
    try:
        # 从token中解码AccessTokenData
        payload_dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = AccessTokenData(**payload_dict)
        user_id = int(token_data.sub)

        # 验证用户是否存在，权限是否够
        user_access_level = get_user_access_level(db, cache, user_id)
        if user_access_level is None:
            raise_unauthorized_exception(user_id={user_id})
        if user_access_level < api_access_level:
            logger.error(f"unauthorized api invocation, {user_id=}")
            raise ServiceError.no_enough_access_level()
        return user_id
    except ExpiredSignatureError as e:
        # token过期
        token_payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False})
        logger.info(f"token expired, {token_payload=}")
        raise e
    except JWTError:
        logger.exception(f"invalid token")
        raise_unauthorized_exception(token=token)


def verify_password(db: Session, staff_id: str, password: str) -> int | None:
    user_auth = crud_user.get_user_auth_by_staff_id(db, staff_id)
    if user_auth is not None and crypt_context.verify(password, user_auth.hashed_password):
        return user_auth.id
    return None
