import logging

from redis import Redis
from sqlalchemy.orm import Session

from app.common.config import config
from app.db import crud

logger = logging.getLogger(__name__)


def get_redis() -> Redis:
    return Redis(host=config.CACHE_HOST, port=config.CACHE_PORT, decode_responses=True)


USER_ACCESS_LEVEL_FORMAT: str = "ual_{}"


def get_user_access_level(db: Session, cache: Redis, user_id: int) -> int | None:
    key = USER_ACCESS_LEVEL_FORMAT.format(user_id)
    access_level: str = cache.get(key)
    if access_level is not None:
        return int(access_level)
    access_level: int | None = crud.get_user_access_level(db, user_id)
    if access_level is None:
        return None
    result = cache.setex(key, config.CACHE_EXPIRE_SECONDS, access_level)
    log_cache(result, f"set user_access_level {{}}, {key}={access_level}")
    return access_level


def invalidate_user_access_level(cache: Redis, user_id: int) -> None:
    key = USER_ACCESS_LEVEL_FORMAT.format(user_id)
    result = cache.delete(key) == 1
    log_cache(result, f"del user_access_level {{}}, key={key}")


def log_cache(is_success: bool, template: str) -> None:
    if is_success:
        logger.info(template.format("success"))
    else:
        logger.error(template.format("failed"))
