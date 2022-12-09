from pathlib import Path
from typing import Any

from pydantic import BaseSettings


class Config(BaseSettings):
    # 是否处于开发环境
    DEBUG_MODE: bool = False

    # 时区，默认
    TIMEZONE: str = "Asia/Shanghai"

    # 数据库URL
    DATABASE_URL: str = "mysql+pymysql://zjlab:zjlab2022@localhost:8100/zj_brain_science_platform"

    # 数据库配置，JSON格式
    DATABASE_CONFIG: dict[str, Any] = {"echo": True}

    # 日志路径
    LOG_ROOT: Path = Path.home() / "log" / "ZJBrainSciencePlatform" / "app"

    # 文件存储路径
    FILE_ROOT: Path = Path.home() / "data" / "ZJBrainSciencePlatform" / "file"

    # 读取文件的块大小
    FILE_CHUNK_SIZE: int = 64 * 1024

    # 日志轮换天数
    LOG_ROTATING_DAYS: int = 7

    # 用户AccessToken有效期，默认7天
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    # 获取最近消息的数量
    GET_RECENT_NOTIFICATIONS_COUNT: int = 10

    # 获取消息列表分页默认大小
    LIST_NOTIFICATIONS_LIMIT: int = 20


config = Config()
