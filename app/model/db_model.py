from datetime import datetime
from enum import Enum

from ormar import Boolean, DateTime, Float, Integer, Model, String, Text
from pydantic import BaseModel

from app.db.database import BaseMeta
from app.timezone_util import utc_now


class ModelMixin:
    # 主键
    id: int = Integer(primary_key=True)
    # 创建时间
    gmt_create: datetime = DateTime(timezone=True, default=utc_now)
    # 修改时间
    gmt_modified: datetime = DateTime(timezone=True, default=utc_now)
    # 该行是否被删除
    is_deleted: bool = Boolean(default=False)


# 用户
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


# 通知
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
    status: str = String(max_length=20, choices=list(Status), default=Status.UNREAD.value)
    # 消息内容
    content: str = Text()


# 实验
class Experiment(Model, ModelMixin):
    class Meta(BaseMeta):
        tablename = "experiment"

    class ExperimentType(Enum):
        SSVEP = "SSVEP"
        MI = "MI"
        NEURON = "neuron"

    # 实验名称
    name: str = String(max_length=255)
    # 实验类型
    type: str = String(max_length=50, choices=list(ExperimentType))
    # 实验地点
    location: str = String(max_length=255)
    # 实验开始时间
    start_at: datetime = DateTime(timezone=True, index=True)
    # 实验结束时间
    end_at: datetime = DateTime(timezone=True)
    # 主操作者，experiment_operator.id
    main_operator: int = Integer(ge=0)
    # 助手，experiment_operator.id
    assistants: list[int] | None
    # 是否为无创实验
    is_non_invasive: bool | None = Boolean(nullable=True)
    # 被试类型
    subject_type: str | None = String(max_length=50, nullable=True)
    # 被试数量
    subject_num: int | None = Integer(minimum=0, nullable=True)
    # 神经元细胞来源部位
    neuron_source: str | None = String(max_length=50, nullable=True)
    # 刺激类型
    stimulation_type: str | None = String(max_length=50, nullable=True)
    # 实验session数量
    session_num: int | None = Integer(minimum=0, nullable=True)
    # 实验trail数量
    trail_num: int | None = Integer(minimum=0, nullable=True)
    # 实验数据是否公开
    is_shared: bool | None = Boolean(nullable=True)


# 实验操作者
class ExperimentAssistant(Model, ModelMixin):
    class Meta(BaseMeta):
        tablename = "experiment_assistant"

    # 用户ID
    user_id: int = Integer(minimum=0)
    # 实验ID
    experiment_id: int = Integer(minimum=0, index=True)


# 文件
class File(Model, ModelMixin):
    class Meta(BaseMeta):
        tablename = "file"

    # 实验ID
    experiment_id: int = Integer(ge=0, index=True)
    # 逻辑路径
    path: str = String(max_length=255, index=True)
    # 文件扩展名（类型）
    extension: str = String(max_length=50)
    # 同一实验下的文件序号
    index: int = Integer(ge=0, index=True)
    # 文件大小（MB）
    size: float = Float(ge=0.0)
    # 是否是设备产生的原始文件
    is_original: bool = Boolean()


# 实验范式
class Paradigm(Model, ModelMixin):
    class Meta(BaseMeta):
        tablename = "paradigm"

    # 实验ID
    experiment_id: int = Integer(ge=0, index=True)
    # 创建者ID
    creator: int = Integer(ge=0)
    # 描述文字
    description: str = Text()


# 实验范式文件
class ParadigmFile(Model, ModelMixin):
    class Meta(BaseMeta):
        tablename = "paradigm_file"

    # 实验范式ID
    paradigm_id: int = Integer(ge=0, index=True)
    # 文件ID
    file_id: int = Integer(ge=0, index=True)
