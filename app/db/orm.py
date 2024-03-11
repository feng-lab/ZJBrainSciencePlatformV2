from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Double, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import expression

from app.db import Base, table_repr
from app.model.enum_filed import (
    ABOBloodType,
    ExperimentType,
    Gender,
    MaritalStatus,
    NotificationStatus,
    NotificationType,
    TaskStatus,
    TaskStepType,
    TaskType,
)

ShortVarChar: String = String(63)
VarChar: String = String(255)


class ModelMixin:
    id: Mapped[int] = mapped_column(Integer, nullable=False, primary_key=True, autoincrement=True, comment="主键")
    gmt_create: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    gmt_modified: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), comment="修改时间")
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=expression.false(), comment="该行是否被删除"
    )


@table_repr
class User(Base, ModelMixin):
    __tablename__ = "user"
    __table_args__ = {"comment": "用户"}

    username: Mapped[str] = mapped_column(String(255), nullable=False, index=True, comment="用户名")
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False, comment="密码哈希")
    staff_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True, comment="员工号")
    last_login_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="上次登录时间")
    last_logout_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="上次下线时间")
    access_level: Mapped[int] = mapped_column(Integer, nullable=False, comment="权限级别")


@table_repr
class Notification(Base, ModelMixin):
    __tablename__ = "notification"
    __table_args__ = {"comment": "通知"}

    gmt_create: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, index=True, server_default=func.now(), comment="创建时间"
    )
    type: Mapped[NotificationType] = mapped_column(Enum(NotificationType), nullable=False, comment="消息类型")
    creator: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False, comment="消息发送者ID")
    receiver: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False, index=True, comment="消息接收者ID")
    status: Mapped[NotificationStatus] = mapped_column(Enum(NotificationStatus), nullable=False, comment="消息状态")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="消息内容")

    creator_user: Mapped[User] = relationship("User", viewonly=True, foreign_keys=[creator])


@table_repr
class ExperimentAssistant(Base):
    __tablename__ = "experiment_assistant"
    __table_args__ = {"comment": "实验助手关系"}

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), primary_key=True)
    experiment_id: Mapped[int] = mapped_column(Integer, ForeignKey("experiment.id"), primary_key=True)


@table_repr
class ExperimentHumanSubject(Base):
    __tablename__ = "experiment_human_subject"
    __table_args__ = {"comment": "实验包含的被试者"}

    experiment_id: Mapped[int] = mapped_column(Integer, ForeignKey("experiment.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("human_subject.user_id"), primary_key=True)


@table_repr
class ExperimentDevice(Base):
    __tablename__ = "experiment_device"
    __table_args__ = {"comment": "实验包含的设备"}

    experiment_id: Mapped[int] = mapped_column(Integer, ForeignKey("experiment.id"), primary_key=True)
    device_id: Mapped[int] = mapped_column(Integer, ForeignKey("device.id"), primary_key=True)
    index: Mapped[int] = mapped_column(Integer, nullable=False, comment="实验内序号")


class ExperimentTag(Base):
    __tablename__ = "experiment_tag"
    __table_args__ = {"comment": "实验标签"}

    experiment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("experiment.id"), nullable=False, primary_key=True, comment="实验ID"
    )
    tag: Mapped[str] = mapped_column(String(50), nullable=False, primary_key=True, comment="标签")


@table_repr
class Experiment(Base, ModelMixin):
    __tablename__ = "experiment"
    __table_args__ = {"comment": "实验"}

    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="实验名称")
    type: Mapped[ExperimentType] = mapped_column(Enum(ExperimentType), nullable=False, comment="实验类型")
    description: Mapped[str] = mapped_column(Text, nullable=False, comment="实验描述")
    location: Mapped[str] = mapped_column(String(255), nullable=False, comment="实验地点")
    start_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True, comment="实验开始时间")
    end_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="实验结束时间")
    main_operator: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False, comment="主操作者ID")
    is_non_invasive: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment="是否为无创实验")
    subject_type: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="被试类型")
    subject_num: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="被试数量")
    neuron_source: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="神经元细胞来源部位")
    stimulation_type: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="刺激类型")
    session_num: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="实验session数量")
    trail_num: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="实验trail数量")
    is_shared: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment="实验是否公开")

    main_operator_obj: Mapped[User] = relationship("User")
    assistants: Mapped[list[User]] = relationship("User", secondary=ExperimentAssistant.__table__)
    human_subjects: Mapped[list["HumanSubject"]] = relationship(
        "HumanSubject", secondary=ExperimentHumanSubject.__table__
    )
    tags: Mapped[list[ExperimentTag]] = relationship("ExperimentTag")
    virtual_files: Mapped[list["VirtualFile"]] = relationship("VirtualFile")
    paradigms: Mapped[list["Paradigm"]] = relationship("Paradigm", viewonly=True)
    exists_paradigms: Mapped[list["Paradigm"]] = relationship(
        "Paradigm",
        viewonly=True,
        primaryjoin="and_(Experiment.id == Paradigm.experiment_id, Paradigm.is_deleted == False, "
        "Experiment.is_deleted == False)",
    )


@table_repr
class StorageFile(Base, ModelMixin):
    __tablename__ = "storage_file"
    __table_args__ = {"comment": "实际文件"}

    virtual_file_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("virtual_file.id"), nullable=False, index=True, comment="虚拟文件ID"
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="文件名")
    size: Mapped[float] = mapped_column(Float, nullable=False, comment="文件大小")
    storage_path: Mapped[str] = mapped_column(String(255), nullable=False, comment="文件系统存储路径")


@table_repr
# class VirtualFile(Base, ModelMixin):
class VirtualFile(Base, ModelMixin):
    __tablename__ = "virtual_file"
    __table_args__ = {"comment": "虚拟文件"}

    experiment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("experiment.id"), nullable=False, index=True, comment="实验ID"
    )
    paradigm_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("paradigm.id"), nullable=True, index=True, comment="范式ID，null表示不属于范式而属于实验"
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="文件名")
    file_type: Mapped[str] = mapped_column(String(50), nullable=False, comment="文件类型")
    is_original: Mapped[bool] = mapped_column(Boolean, nullable=False, comment="是否是设备产生的原始文件")
    size: Mapped[float] = mapped_column(Float, nullable=False, comment="显示给用户看的文件大小")

    storage_files: Mapped[list[StorageFile]] = relationship(StorageFile, viewonly=True)
    exist_storage_files: Mapped[list[StorageFile]] = relationship(
        StorageFile,
        primaryjoin="and_(VirtualFile.id == StorageFile.virtual_file_id, StorageFile.is_deleted == False, "
        "VirtualFile.is_deleted == False)",
        viewonly=True,
    )


@table_repr
class Paradigm(Base, ModelMixin):
    __tablename__ = "paradigm"
    __table_args__ = {"comment": "实验范式"}

    experiment_id: Mapped[int] = mapped_column(Integer, ForeignKey("experiment.id"), nullable=False, comment="实验ID")
    creator: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False, comment="创建者ID")
    description: Mapped[str | None] = mapped_column(Text(), nullable=False, comment="描述文字")

    virtual_files: Mapped[list[VirtualFile]] = relationship(VirtualFile, viewonly=True)
    exist_virtual_files: Mapped[list[VirtualFile]] = relationship(
        VirtualFile,
        viewonly=True,
        primaryjoin="and_(Paradigm.id == VirtualFile.paradigm_id, VirtualFile.is_deleted == False, "
        "Paradigm.is_deleted == False)",
    )
    creator_obj: Mapped[User] = relationship("User")


@table_repr
class Device(Base, ModelMixin):
    __tablename__ = "device"
    __table_args__ = {"comment": "实验设备"}

    brand: Mapped[str] = mapped_column(String(255), nullable=False, comment="设备品牌")
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="设备名称")
    purpose: Mapped[str] = mapped_column(String(255), nullable=False, comment="设备用途")

    experiments: Mapped[list[Experiment]] = relationship("Experiment", secondary=ExperimentDevice.__table__)


@table_repr
class HumanSubject(Base, ModelMixin):
    __tablename__ = "human_subject"
    __table_args__ = {"comment": "被试者"}

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False, unique=True, index=True, comment="用户ID"
    )
    name: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="姓名")
    gender: Mapped[Gender | None] = mapped_column(Enum(Gender), nullable=True, comment="性别")
    birthdate: Mapped[date | None] = mapped_column(Date, nullable=True, comment="出生日期")
    death_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment="死亡日期")
    education: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="教育程度")
    occupation: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="职业")
    marital_status: Mapped[MaritalStatus | None] = mapped_column(Enum(MaritalStatus), nullable=True, comment="婚姻状况")
    abo_blood_type: Mapped[ABOBloodType | None] = mapped_column(Enum(ABOBloodType), nullable=True, comment="ABO血型")
    is_left_handed: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment="是否是左撇子")
    phone_number: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="电话号码")
    email: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="电子邮箱地址")
    address: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="住址")

    user: Mapped[User] = relationship("User")


@table_repr
class HumanSubjectIndex(Base):
    __tablename__ = "human_subject_index"
    __table_args__ = {"comment": "被试者用户序号"}

    index: Mapped[int] = mapped_column(Integer, primary_key=True, comment="下一个被试者的序号")


@table_repr
class Task(Base, ModelMixin):
    __tablename__ = "task"
    __table_args__ = {"comment": "任务"}

    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="任务名")
    description: Mapped[str] = mapped_column(Text, nullable=False, comment="任务描述")
    source_file: Mapped[int] = mapped_column(
        Integer, ForeignKey("virtual_file.id"), nullable=False, comment="任务分析的文件ID"
    )
    type: Mapped[TaskType] = mapped_column(Enum(TaskType), nullable=False, comment="任务类型")
    start_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="任务开始执行的时间")
    end_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="任务结束时间")
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), nullable=False, comment="任务状态")
    creator: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False, comment="任务创建者ID")

    steps: Mapped[list["TaskStep"]] = relationship("TaskStep")
    creator_obj: Mapped[User] = relationship("User")


@table_repr
class TaskStep(Base, ModelMixin):
    __tablename__ = "task_step"
    __table_args__ = {"comment": "任务步骤"}

    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("task.id"), nullable=False, comment="任务ID")
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="步骤名字")
    type: Mapped[TaskStepType] = mapped_column(Enum(TaskStepType), nullable=False, comment="任务步骤类型")
    parameter: Mapped[str] = mapped_column(Text, nullable=False, comment="步骤参数JSON")
    index: Mapped[int] = mapped_column(Integer, nullable=False, comment="任务中的步骤顺序")
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), nullable=False, comment="步骤状态")
    start_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="步骤开始执行的时间")
    end_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="步骤结束时间")
    result_file_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("virtual_file.id"), nullable=True, comment="结果文件ID"
    )
    error_msg: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="错误信息")


class AtlasComponentMixin:
    atlas_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="所属图谱ID")


class TreeNodeMixin(ModelMixin):
    parent_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="父节点ID，null表示第一层节点")


@table_repr
class Atlas(Base, ModelMixin):
    __tablename__ = "atlas"
    __table_args__ = {"comment": "脑图谱"}

    name: Mapped[str] = mapped_column(VarChar, nullable=False, comment="名称")
    url: Mapped[str] = mapped_column(VarChar, nullable=False, comment="主页地址")
    title: Mapped[str] = mapped_column(VarChar, nullable=False, comment="页面显示的标题")
    whole_segment_id: Mapped[int] = mapped_column(BigInteger, nullable=True, comment="全脑轮廓ID")


@table_repr
class AtlasRegion(Base, TreeNodeMixin, AtlasComponentMixin):
    __tablename__ = "atlas_region"
    __table_args__ = {"comment": "脑图谱脑区构成信息，以树状结构存储"}

    region_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="脑区ID")
    description: Mapped[str] = mapped_column(VarChar, nullable=False, comment="描述")
    acronym: Mapped[str] = mapped_column(VarChar, nullable=False, comment="缩写")
    lobe: Mapped[str | None] = mapped_column(VarChar, nullable=True, comment="所属脑叶")
    gyrus: Mapped[str | None] = mapped_column(VarChar, nullable=True, comment="所属脑回")
    label: Mapped[str] = mapped_column(VarChar, nullable=True, comment="标签")


@table_repr
class AtlasRegionLink(Base, ModelMixin, AtlasComponentMixin):
    __tablename__ = "atlas_region_link"
    __table_args__ = {"comment": "脑图谱脑区之间的连接强度信息"}

    link_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="连接信息ID")
    region1: Mapped[str] = mapped_column(VarChar, nullable=False, comment="脑区1")
    region2: Mapped[str] = mapped_column(VarChar, nullable=False, comment="脑区2")
    value: Mapped[float | None] = mapped_column(Double, nullable=True, comment="连接强度，null表示仅有连接")
    opposite_value: Mapped[float | None] = mapped_column(Double, nullable=True, comment="反向连接强度，null表示仅有连接")


@table_repr
class AtlasBehavioralDomain(Base, TreeNodeMixin, AtlasComponentMixin):
    __tablename__ = "atlas_behavioral_domain"
    __table_args__ = {"comment": "脑图谱的行为域结构数据，以树状结构存储"}

    name: Mapped[str] = mapped_column(VarChar, nullable=False, comment="名称")
    value: Mapped[float] = mapped_column(Double, nullable=False, comment="值")
    label: Mapped[str] = mapped_column(VarChar, nullable=False, comment="显示的名字")
    description: Mapped[str] = mapped_column(Text, nullable=True, comment="描述")


@table_repr
class AtlasRegionBehavioralDomain(Base, ModelMixin, AtlasComponentMixin):
    __tablename__ = "atlas_region_behavioral_domain"
    __table_args__ = {"comment": "脑图谱中与脑区相关联的行为域数据"}

    key: Mapped[str] = mapped_column(VarChar, nullable=False, comment="行为域")
    value: Mapped[float] = mapped_column(Double, nullable=False, comment="行为域值")
    region_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="脑区ID")


@table_repr
class AtlasParadigmClass(Base, TreeNodeMixin, AtlasComponentMixin):
    __tablename__ = "atlas_paradigm_class"
    __table_args__ = {"comment": "脑图谱范例集"}

    name: Mapped[str] = mapped_column(VarChar, nullable=False, comment="名称")
    value: Mapped[float] = mapped_column(Double, nullable=False, comment="值")
    label: Mapped[str] = mapped_column(VarChar, nullable=False, comment="标签")
    description: Mapped[str] = mapped_column(Text, nullable=False, comment="描述")


@table_repr
class AtlasRegionParadigmClass(Base, ModelMixin, AtlasComponentMixin):
    __tablename__ = "atlas_region_paradigm_class"
    __table_args__ = {"comment": "脑图谱中与脑区相关联的范例集"}

    key: Mapped[str] = mapped_column(VarChar, nullable=False, comment="范例集")
    value: Mapped[float] = mapped_column(Double, nullable=False, comment="范例集值")
    region_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="脑区ID")

class Dataset(Base,ModelMixin):
    __tablename__ = "Dataset"
    __table_args__ = {"comment": "数据集"}

    user_id : Mapped[int] = mapped_column(Integer, ForeignKey("user.id"),  primary_key=True)
    # created_at : Mapped[DateTime] = mapped_column(DateTime, nullable=False,index=True, erver_default=func.now(), comment="创建时间")
    # modified_at : Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=func.now(), comment="修改时间")
    # is_deleted : Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=expression.false(), comment="该行是否被删除")

    description: Mapped[str] = mapped_column(Text, nullable=False, comment="描述")
    species: Mapped[str | None] = mapped_column(Text, nullable=True, comment="物种")
    paper_title : Mapped[str | None] = mapped_column(Text, nullable=True, comment="文章标题")
    paper_doi : Mapped[str | None] = mapped_column(Text, nullable=True, comment="文章DOI")
    development_stage : Mapped[str | None] = mapped_column(Text, nullable=False, comment="发育时期")
    file_format : Mapped[str | None] = mapped_column(Text, nullable=True, comment="文件格式")
    sample_size : Mapped[int | None] = mapped_column(Integer, nullable=True, comment="样本数量")
    data_publisher :  Mapped[str | None]  = mapped_column(Text, nullable=True, comment="数据发布机构/单位")
    date_update_year :  Mapped[str | None] = mapped_column(DateTime, nullable=True, comment="数据更新年份")
    file_count : Mapped[float | None] = mapped_column(Float, nullable=True, comment="文件数量")
    file_total_size_gb :  Mapped[float | None] = mapped_column(Float, nullable=True, comment="数据总量(GB)")
    file_acquired_size_gb : Mapped[float | None] = mapped_column(Float, nullable=True, comment="以获取数据(GB)")
    associated_diseases : Mapped[str | None] = mapped_column(Text, nullable=False, comment="相关疾病")
    organ : Mapped[str| None] = mapped_column(Text, nullable=True, comment="器官")
    cell_count : Mapped[int | None] = mapped_column(Integer, nullable=True, comment="细胞数")
    data_type : Mapped[str | None] = mapped_column(Text, nullable=True, comment="数据类型")
    experiment_platform : Mapped[str | None] = mapped_column(Text, nullable=True, comment="实验、测序平台")
    fetch_url : Mapped[str | None] = mapped_column(Text, nullable=True, comment="下载路径")
    project : Mapped[str | None] = mapped_column(Text, nullable=True, comment="项目")

class DatasetFile(Base,ModelMixin):
    __tablename__ = "DatasetFile"
    __table_args__ = {"comment": "数据集文件"}

    # user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), primary_key=True, comment="用户id")
    # created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False,index=True, erver_default=func.now(), comment="创建时间")
    # modified_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=func.now(),
    #                                               comment="修改时间")
    # is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=expression.false(),
    #                                          comment="该行是否被删除")
    path: Mapped[str] = mapped_column(Text, nullable=False, comment="文件路径")
    dataset_id: Mapped[int] = mapped_column(Integer, ForeignKey("Dataset.id"),  nullable=False, index=True,comment="数据集id")
