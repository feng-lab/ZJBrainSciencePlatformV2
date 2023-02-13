from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import Boolean, Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import expression

from app.db import Base, table_repr


class ModelMixin:
    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, autoincrement=True, comment="主键"
    )
    gmt_create: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="创建时间"
    )
    gmt_modified: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="修改时间"
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=expression.false(), comment="该行是否被删除"
    )


@table_repr
class User(Base, ModelMixin):
    __tablename__ = "user"
    __table_args__ = {"comment": "用户"}

    username: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, unique=True, comment="用户名"
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False, comment="密码哈希")
    staff_id: Mapped[str] = mapped_column(String(255), nullable=False, comment="员工号")
    last_login_time: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="上次登录时间"
    )
    last_logout_time: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="上次下线时间"
    )
    access_level: Mapped[int] = mapped_column(Integer, nullable=False, comment="权限级别")


@table_repr
class Notification(Base, ModelMixin):
    __tablename__ = "notification"
    __table_args__ = {"comment": "通知"}

    class Status(StrEnum):
        unread = "unread"
        read = "read"

    class Type(StrEnum):
        task_step_status = "task_step_status"

    gmt_create: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, index=True, server_default=func.now(), comment="创建时间"
    )
    type: Mapped[Type] = mapped_column(Enum(Type), nullable=False, comment="消息类型")
    creator: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False, comment="消息发送者ID"
    )
    receiver: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False, index=True, comment="消息接收者ID"
    )
    status: Mapped[Status] = mapped_column(Enum(Status), nullable=False, comment="消息状态")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="消息内容")


@table_repr
class ExperimentAssistant(Base):
    __tablename__ = "experiment_assistant"
    __table_args__ = {"comment": "实验助手关系"}

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), primary_key=True)
    experiment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("experiment.id"), primary_key=True
    )


@table_repr
class ExperimentHumanSubject(Base):
    __tablename__ = "experiment_human_subject"
    __table_args__ = {"comment": "实验包含的被试者"}

    experiment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("experiment.id"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("human_subject.user_id"), primary_key=True
    )


@table_repr
class Experiment(Base, ModelMixin):
    __tablename__ = "experiment"
    __table_args__ = {"comment": "实验"}

    class Type(StrEnum):
        SSVEP = "SSVEP"
        MI = "MI"
        neuron = "neuron"

    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="实验名称")
    type: Mapped[Type] = mapped_column(Enum(Type), nullable=False, comment="实验类型")
    description: Mapped[str] = mapped_column(Text, nullable=False, comment="实验描述")
    location: Mapped[str] = mapped_column(String(255), nullable=False, comment="实验地点")
    start_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, index=True, comment="实验开始时间"
    )
    end_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="实验结束时间")
    main_operator: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False, comment="主操作者ID"
    )
    is_non_invasive: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment="是否为无创实验")
    subject_type: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="被试类型")
    subject_num: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="被试数量")
    neuron_source: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="神经元细胞来源部位"
    )
    stimulation_type: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="刺激类型")
    session_num: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="实验session数量")
    trail_num: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="实验trail数量")
    is_shared: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment="实验是否公开")

    main_operator_obj: Mapped[User] = relationship("User")
    assistants: Mapped[list[User]] = relationship("User", secondary=ExperimentAssistant.__table__)
    human_subjects: Mapped[list["HumanSubject"]] = relationship(
        "HumanSubject", secondary=ExperimentHumanSubject.__table__
    )


@table_repr
class File(Base, ModelMixin):
    __tablename__ = "file"
    __table_args__ = {"comment": "文件"}

    experiment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("experiment.id"), nullable=False, index=True, comment="实验ID"
    )
    paradigm_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("paradigm.id"),
        nullable=True,
        index=True,
        comment="范式ID，null表示不属于范式而属于实验",
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="逻辑路径")
    extension: Mapped[str] = mapped_column(String(50), nullable=False, comment="文件扩展名")
    index: Mapped[int] = mapped_column(Integer, nullable=False, index=True, comment="同一实验下的文件序号")
    size: Mapped[float] = mapped_column(Float, nullable=False, comment="同一实验下的文件序号")
    is_original: Mapped[bool] = mapped_column(Boolean, nullable=False, comment="是否是设备产生的原始文件")


@table_repr
class Paradigm(Base, ModelMixin):
    __tablename__ = "paradigm"
    __table_args__ = {"comment": "实验范式"}

    experiment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("experiment.id"), nullable=False, comment="实验ID"
    )
    creator: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False, comment="创建者ID"
    )
    description: Mapped[str | None] = mapped_column(Text(), nullable=False, comment="描述文字")

    files: Mapped[list[File]] = relationship("File")
    creator_obj: Mapped[User] = relationship("User")


@table_repr
class Device(Base, ModelMixin):
    __tablename__ = "device"
    __table_args__ = {"comment": "实验设备"}

    experiment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("experiment.id"), nullable=False, index=True, comment="实验ID"
    )
    brand: Mapped[str] = mapped_column(String(255), nullable=False, comment="设备品牌")
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="设备名称")
    purpose: Mapped[str] = mapped_column(String(255), nullable=False, comment="设备用途")
    index: Mapped[int] = mapped_column(Integer, nullable=False, comment="实验内序号")


class Gender(StrEnum):
    male = "male"
    female = "female"


class MaritalStatus(StrEnum):
    unmarried = "unmarried"
    married = "married"


class ABOBloodType(StrEnum):
    A = "A"
    B = "B"
    AB = "AB"
    O = "O"


@table_repr
class HumanSubject(Base, ModelMixin):
    __tablename__ = "human_subject"
    __table_args__ = {"comment": "被试者"}

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False, unique=True, index=True, comment="用户ID"
    )
    gender: Mapped[Gender | None] = mapped_column(Enum(Gender), nullable=True, comment="性别")
    birthdate: Mapped[date | None] = mapped_column(Date, nullable=True, comment="出生日期")
    death_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment="死亡日期")
    education: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="教育程度")
    occupation: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="职业")
    marital_status: Mapped[MaritalStatus | None] = mapped_column(
        Enum(MaritalStatus), nullable=True, comment="婚姻状况"
    )
    abo_blood_type: Mapped[ABOBloodType | None] = mapped_column(
        Enum(ABOBloodType), nullable=True, comment="ABO血型"
    )
    is_left_handed: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment="是否是左撇子")
    phone_number: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="电话号码")
    email: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="电子邮箱地址")
    address: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="住址")

    user: Mapped[User] = relationship("User")
