import logging

from redis import Redis
from sqlalchemy.orm import Session

from app.common.config import config
from app.db import crud

logger = logging.getLogger(__name__)


def get_redis() -> Redis:
    return Redis(
        host=config.CACHE_HOST,
        port=config.CACHE_PORT,
        decode_responses=True
    )


USER_ACCESS_LEVEL_FORMAT: str = "ual_{}"


def get_user_access_level(db: Session, cache: Redis, user_id: int) -> int | None:
    key = USER_ACCESS_LEVEL_FORMAT.format(user_id)
    access_level: str = cache.get(key)
    if access_level is not None:
        return int(access_level)
    access_level: int | None = crud.get_user_access_level(db, user_id)
    if access_level is None:
        return None
    if cache.setex(key, config.CACHE_EXPIRE_SECONDS, access_level):
        logger.info(f"write cache success, {key}={access_level}")
    else:
        logger.error(f"write cache failed, {key}={access_level}")
    return access_level
