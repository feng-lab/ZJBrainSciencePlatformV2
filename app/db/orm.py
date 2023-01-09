import itertools
from enum import StrEnum
from typing import Any

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, Integer, String, Text, func
from sqlalchemy.sql import expression

from app.db import Base


class ModelMixin:
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True, comment="主键")
    gmt_create = Column(
        DateTime, nullable=False, index=True, server_default=func.now(), comment="创建时间"
    )
    gmt_modified = Column(DateTime, nullable=False, server_default=func.now(), comment="修改时间")
    is_deleted = Column(
        Boolean, nullable=False, server_default=expression.false(), comment="该行是否被删除"
    )

    def make_repr(self, **fields: Any) -> str:
        common_fields = {
            "id": self.id,
            "gmt_create": self.gmt_create,
            "gmt_modified": self.gmt_modified,
            "is_deleted": self.is_deleted,
        }
        field_strs = [
            f"{field_name}={field_value!r}"
            for field_name, field_value in itertools.chain(common_fields.items(), fields.items())
        ]
        class_name = self.__class__.__name__
        return f"<{class_name}:{','.join(field_strs)}>"


class User(Base, ModelMixin):
    __tablename__ = "user"
    __table_args__ = {"comment": "用户"}

    username = Column(String(255), nullable=False, index=True, unique=True, comment="用户名")
    hashed_password = Column(String(255), nullable=False, comment="密码哈希")
    staff_id = Column(String(255), nullable=False, comment="员工号")
    last_login_time = Column(DateTime, nullable=True, comment="上次登录时间")
    last_logout_time = Column(DateTime, nullable=True, comment="上次下线时间")
    access_level = Column(Integer, nullable=False, comment="权限级别")

    def __repr__(self):
        return self.make_repr(
            username=self.username,
            hashed_password=self.hashed_password,
            staff_id=self.staff_id,
            last_login_time=self.last_login_time,
            last_logout_time=self.last_logout_time,
            access_level=self.access_level,
        )


class Notification(Base, ModelMixin):
    __tablename__ = "notification"
    __table_args__ = {"comment": "通知"}

    class Status(StrEnum):
        unread = "unread"
        read = "read"

    class Type(StrEnum):
        task_step_status = "task_step_status"

    type = Column(Enum(Type), nullable=False, comment="消息类型")
    creator = Column(Integer, nullable=False, comment="消息发送者ID")
    receiver = Column(Integer, nullable=False, index=True, comment="消息接收者ID")
    status = Column(Enum(Status), nullable=False, comment="消息状态")
    content = Column(Text, nullable=False, comment="消息内容")

    def __repr__(self):
        return self.make_repr(
            type=self.type,
            creator=self.creator,
            receiver=self.receiver,
            status=self.status,
            content=self.content,
        )


class Experiment(Base, ModelMixin):
    __tablename__ = "experiment"
    __table_args__ = {"comment": "实验"}

    class Type(StrEnum):
        SSVEP = "SSVEP"
        MI = "MI"
        neuron = "neuron"

    name = Column(String(255), nullable=False, comment="实验名称")
    type = Column(Enum(Type), nullable=False, comment="实验类型")
    description = Column(Text, nullable=False, comment="实验描述")
    location = Column(String(255), nullable=False, comment="实验地点")
    start_at = Column(DateTime, nullable=False, index=True, comment="实验开始时间")
    end_at = Column(DateTime, nullable=False, comment="实验结束时间")
    main_operator = Column(Integer, nullable=False, comment="主操作者ID")
    is_non_invasive = Column(Boolean, nullable=True, comment="是否为无创实验")
    subject_type = Column(String(50), nullable=True, comment="被试类型")
    subject_num = Column(Integer, nullable=True, comment="被试数量")
    neuron_source = Column(String(50), nullable=True, comment="神经元细胞来源部位")
    stimulation_type = Column(String(50), nullable=True, comment="刺激类型")
    session_num = Column(Integer, nullable=True, comment="实验session数量")
    trail_num = Column(Integer, nullable=True, comment="实验trail数量")
    is_shared = Column(Boolean, nullable=True, comment="实验是否公开")

    def __repr__(self) -> str:
        return self.make_repr(
            name=self.name,
            type=self.type,
            description=self.description,
            location=self.location,
            start_at=self.start_at,
            end_at=self.end_at,
            main_operator=self.main_operator,
            is_non_invasive=self.is_non_invasive,
            subject_type=self.subject_type,
            subject_num=self.subject_num,
            neuron_source=self.neuron_source,
            stimulation_type=self.stimulation_type,
            session_num=self.session_num,
            trail_num=self.trail_num,
            is_shared=self.is_shared,
        )


class ExperimentAssistant(Base, ModelMixin):
    __tablename__ = "experiment_assistant"
    __table_args__ = {"comment": "实验助手"}

    user_id = Column(Integer, nullable=False)
    experiment_id = Column(Integer, nullable=False, index=True)

    def __repr__(self):
        return self.make_repr(user_id=self.user_id, experiment_id=self.experiment_id)


class File(Base, ModelMixin):
    __tablename__ = "file"
    __table_args__ = {"comment": "文件"}

    experiment_id = Column(Integer, nullable=False, index=True, comment="实验ID")
    name = Column(String(255), nullable=False, comment="逻辑路径")
    extension = Column(String(50), nullable=False, comment="文件扩展名")
    index = Column(Integer, nullable=False, index=True, comment="同一实验下的文件序号")
    size = Column(Float, nullable=False, comment="同一实验下的文件序号")
    is_original = Column(Boolean, nullable=False, comment="是否是设备产生的原始文件")

    def __repr__(self):
        return self.make_repr(
            experiment_id=self.experiment_id,
            name=self.name,
            extension=self.extension,
            index=self.index,
            size=self.size,
            is_original=self.is_original,
        )


class Paradigm(Base, ModelMixin):
    __tablename__ = "paradigm"
    __table_args__ = {"comment": "实验范式"}

    experiment_id = Column(Integer, nullable=False, index=True, comment="实验ID")
    creator = Column(Integer, nullable=False, comment="创建者ID")
    description = Column(Text(), nullable=False, comment="描述文字")

    def __repr__(self):
        return self.make_repr(
            experiment_id=self.experiment_id, creator=self.creator, description=self.description
        )


class ParadigmFile(Base, ModelMixin):
    __tablename__ = "paradigm_file"
    __table_args__ = {"comment": "实验范式文件"}

    paradigm_id = Column(Integer, nullable=False, index=True, comment="实验范式ID")
    file_id = Column(Integer, nullable=False, comment="文件ID")

    def __repr__(self):
        return self.make_repr(paradigm_id=self.paradigm_id, file_id=self.file_id)
