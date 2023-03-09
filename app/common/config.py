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

    # 图片文件后缀
    IMAGE_FILE_EXTENSIONS: list[str] = ["jpg", "jpeg", "png", "webp", "bmp", "gif"]

    # 日志轮换天数
    LOG_ROTATING_DAYS: int = 7

    # 用户AccessToken有效期，默认7天
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    # 获取最近消息的数量
    GET_RECENT_NOTIFICATIONS_COUNT: int = 10

    # 算法GRPC服务的地址
    ALGORITHM_GRPC_ADDRESS: str = "localhost"

    # 算法GRPC服务的端口
    ALGORITHM_GRPC_PORT: int = 12345

    # Redis缓存地址
    CACHE_HOST: str = "localhost"

    # Redis缓存端口
    CACHE_PORT: int = 8200

    # Redis缓存默认失效时间，默认一天
    CACHE_EXPIRE_SECONDS: int = 24 * 60 * 60

    def get_algorithm_grpc_address(self):
        return f"{self.ALGORITHM_GRPC_ADDRESS}:{self.ALGORITHM_GRPC_PORT}"

    # 数据库链接心跳检测间隔
    DATABASE_HEARTBEAT_INTERVAL_SECONDS: float = 3 * 60


config = Config()
print(config.json())
