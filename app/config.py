from functools import lru_cache
from typing import Any

from pydantic import BaseSettings


class Config(BaseSettings):
    # 数据库URL
    DATABASE_URL: str

    # 数据库配置，JSON格式
    DATABASE_CONFIG: dict[str, Any] = {}

    # 是否处于开发环境
    DEBUG_MODE: bool = False


@lru_cache
def get_config():
    return Config()
