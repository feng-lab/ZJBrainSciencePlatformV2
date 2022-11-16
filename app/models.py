from datetime import datetime

import databases
import sqlalchemy
from ormar import Model, ModelMeta, String, DateTime, Boolean, Integer
from sqlalchemy import func

from app.config import get_config

metadata = sqlalchemy.MetaData()
database = databases.Database(get_config().DATABASE_URL)


class BaseMeta(ModelMeta):
    database = database
    metadata = metadata


class ModelMixin:
    # 主键
    id: int = Integer(primary_key=True)
    # 创建时间
    gmt_create: datetime = DateTime(timezone=True, server_default=func.now())
    # 修改时间
    gmt_modified: datetime = DateTime(timezone=True, server_default=func.now())
    # 该行是否被删除
    is_deleted: bool = Boolean(default=False)


class User(Model, ModelMixin):
    class Meta(BaseMeta):
        tablename = "user"

    # 用户名
    username: str = String(max_length=255, index=True, unique=True)
    # 密码哈希
    hashed_password: str = String(max_length=255)
    # 员工号
    staff_id: str = String(max_length=255, index=True)
    # 账户类别
    account_type: str = String(max_length=255)
    # 上次登录时间
    last_login_time: datetime | None = DateTime(timezone=True, nullable=True)
    # 上次下线时间
    last_logout_time: datetime | None = DateTime(timezone=True, nullable=True)

    def __repr__(self):
        return (
            f"User(id={self.id!r},username={self.username!r},hashed_password={self.hashed_password!r},"
            f"staff_id={self.staff_id!r},account_type={self.account_type!r},last_login_time={self.last_login_time!r},"
            f"last_logout_time={self.last_logout_time!r},gmt_create={self.gmt_create!r},"
            f"gmt_modified={self.gmt_modified!r},is_deleted={self.is_deleted!r})"
        )


engine = sqlalchemy.create_engine(
    get_config().DATABASE_URL, **get_config().DATABASE_CONFIG
)
metadata.create_all(engine)
