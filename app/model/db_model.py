from datetime import datetime
from enum import Enum

from ormar import Model, String, DateTime, Boolean, Integer, Text
from pydantic import BaseModel

from app.db.database import BaseMeta
from app.utils import utc_now


class ModelMixin:
    # 主键
    id: int = Integer(primary_key=True)
    # 创建时间
    gmt_create: datetime = DateTime(timezone=True, default=utc_now)
    # 修改时间
    gmt_modified: datetime = DateTime(timezone=True, default=utc_now)
    # 该行是否被删除
    is_deleted: bool = Boolean(default=False)


class User(Model, ModelMixin):
    class Meta(BaseMeta):
        tablename = "user"

    # 用户名
    username: str = String(max_length=255, index=True)
    # 密码哈希
    hashed_password: str = String(max_length=255)
    # 员工号
    staff_id: str = String(max_length=255)
    # 上次登录时间
    last_login_time: datetime | None = DateTime(timezone=True, nullable=True)
    # 上次下线时间
    last_logout_time: datetime | None = DateTime(timezone=True, nullable=True)
    # 权限级别
    access_level: int = Integer(minimum=0)


class Notification(Model, ModelMixin):
    class Meta(BaseMeta):
        tablename = "notification"

    class Status(Enum):
        UNREAD = "unread"
        READ = "read"

    class Type(Enum):
        TASK_STEP_STATUS = "task_step_status"

    class TaskStepStatusNotification(BaseModel):
        task_id: int
        task_name: str
        task_status: int

    # 消息类型
    type: str = String(max_length=20, choices=list(Type))
    # 消息发送者ID
    creator: int = Integer()
    # 消息接收者ID
    receiver: int = Integer(index=True)
    # 消息发送时间
    # 该字段指消息发送的时间，gmt_create指数据表记录创建时间
    create_at: datetime = DateTime(timezone=True, index=True)
    # 消息状态
    status: str = String(
        max_length=20, choices=list(Status), default=Status.UNREAD.value
    )
    # 消息内容
    content: str = Text()