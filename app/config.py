from functools import lru_cache
from typing import Any

from pydantic import BaseSettings


class Config(BaseSettings):
    # 是否处于开发环境
    DEBUG_MODE: bool = False

    # 数据库URL
    DATABASE_URL: str

    # 数据库配置，JSON格式
    DATABASE_CONFIG: dict[str, Any] = {}

    # 用户AccessToken有效期，默认7天
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7


@lru_cache
def get_config():
    return Config()
