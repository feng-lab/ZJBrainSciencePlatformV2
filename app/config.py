from typing import Any

from pydantic import BaseSettings


class Config(BaseSettings):
    DATABASE_URL: str
    DATABASE_CONFIG: dict[str, Any] = {}
    DEBUG_MODE: bool = False


config = Config()
