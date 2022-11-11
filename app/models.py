from sqlalchemy import Column, String, BigInteger, Boolean, func, TIMESTAMP, Text, Date
from sqlalchemy.sql import expression

from app.database import Base


class LoginMaster(Base):
    __tablename__ = "login_master"

    id = Column("id", BigInteger, primary_key=True, comment="主键")
    user_account = Column(
        "user_account", String(length=255), nullable=False, comment="用户名"
    )
    password = Column("password", String(length=255), nullable=False, comment="密码")
    staff_id = Column("staff_id", String(length=255), nullable=False, comment="员工号")
    account_type = Column(
        "account_type", String(length=255), nullable=False, comment="账户类别"
    )
    last_login_time = Column(
        "last_login_time", TIMESTAMP, nullable=True, comment="上次登录时间(UTC)"
    )
    last_logout_time = Column(
        "last_logout_time", TIMESTAMP, nullable=True, comment="上次下线时间(UTC)"
    )
    gmt_create = Column(
        "gmt_create",
        TIMESTAMP,
        nullable=False,
        server_default=func.utcnow(),
        comment="创建时间(UTC)",
    )
    gmt_modified = Column(
        "gmt_modified",
        TIMESTAMP,
        nullable=False,
        server_default=func.utcnow(),
        onupdate=func.utcnow(),
        comment="最近修改时间(UTC)",
    )
    is_deleted = Column(
        "is_deleted",
        Boolean,
        nullable=False,
        server_default=expression.false(),
        comment="记录是否被删除",
    )

    def __repr__(self):
        return (
            f"LoginMaster(id={self.id!r},user_account={self.user_account!r},password={self.password!r},"
            f"staff_id={self.staff_id!r},account_type={self.account_type!r},last_login_time={self.last_login_time!r},"
            f"last_logout_time={self.last_logout_time!r},gmt_create={self.gmt_create!r},"
            f"gmt_modified={self.gmt_modified!r},is_deleted={self.is_deleted!r})"
        )


class StaffMaster(Base):
    __tablename__ = "staff_master"

    id = Column("id", BigInteger, primary_key=True, comment="主键")
    staff_id = Column("staff_id", String(length=255), nullable=False, comment="员工号")
    staff_name = Column(
        "staff_name", String(length=255), nullable=False, comment="人员名称"
    )
    staff_type = Column(
        "staff_type", String(length=255), nullable=False, comment="人员类别"
    )
    staff_status = Column(
        "staff_status", String(length=20), nullable=False, comment="员工状态，在职或离职"
    )
    institution = Column(
        "institution", String(length=255), nullable=False, comment="所属机构"
    )
    creator_id = Column(
        "creator_id", String(length=255), nullable=False, comment="创建人编号，若为自己创建，则为0"
    )
    email = Column("email", String(length=255), comment="联系邮箱")
    cellphone_number = Column("cellphone_number", String(length=50), comment="手机号码")
    gmt_create = Column(
        "gmt_create",
        TIMESTAMP,
        nullable=False,
        server_default=func.utcnow(),
        comment="创建时间(UTC)",
    )
    gmt_modified = Column(
        "gmt_modified",
        TIMESTAMP,
        nullable=False,
        server_default=func.utcnow(),
        onupdate=func.utcnow(),
        comment="最近修改时间(UTC)",
    )
    is_deleted = Column(
        "is_deleted",
        Boolean,
        nullable=False,
        server_default=expression.false(),
        comment="记录是否被删除",
    )

    def __repr__(self):
        return (
            f"StaffMaster(id={self.id!r},staff_id={self.staff_id!r},staff_name={self.staff_name!r},"
            f"staff_type={self.staff_type!r},staff_status={self.staff_status!r},institution={self.institution!r},"
            f"creator_id={self.creator_id!r},email={self.email!r},cellphone_number={self.cellphone_number!r},"
            f"gmt_create={self.gmt_create!r},gmt_modified={self.gmt_modified!r},is_deleted={self.is_deleted!r})"
        )


class Message(Base):
    __tablename__ = "message"

    id = Column("id", BigInteger, primary_key=True, comment="主键")
    sender_id = Column(
        "sender_id", String(length=255), nullable=False, comment="消息发送者，系统或用户"
    )
    receiver_id = Column(
        "receiver_id", String(length=255), nullable=False, comment="消息接收者"
    )
    msg_type = Column(
        "msg_type", String(length=20), nullable=False, comment="消息的类型，警告、提示、消息等"
    )
    msg_status = Column("msg_status", String(length=20), nullable=False, comment="消息状态")
    content = Column("content", Text, nullable=False, comment="消息内容")
    gmt_create = Column(
        "gmt_create",
        TIMESTAMP,
        nullable=False,
        server_default=func.utcnow(),
        comment="创建时间(UTC)",
    )
    gmt_modified = Column(
        "gmt_modified",
        TIMESTAMP,
        nullable=False,
        server_default=func.utcnow(),
        onupdate=func.utcnow(),
        comment="最近修改时间(UTC)",
    )
    is_deleted = Column(
        "is_deleted",
        Boolean,
        nullable=False,
        server_default=expression.false(),
        comment="记录是否被删除",
    )

    def __repr__(self):
        return (
            f"Message(id={self.id!r},sender_id={self.sender_id!r},receiver_id={self.receiver_id!r},"
            f"msg_type={self.msg_type!r},msg_status={self.msg_status!r},content={self.content!r},"
            f"gmt_create={self.gmt_create!r},gmt_modified={self.gmt_modified!r},is_deleted={self.is_deleted!r})"
        )


class SubjectHuman(Base):
    __tablename__ = "subject_human"

    id = Column("id", BigInteger, primary_key=True, comment="主键")
    subject_id = Column(
        "subject_id",
        String(length=255),
        nullable=False,
        unique=True,
        index=True,
        comment="实验对象的唯一识别编号，系统自动生成",
    )
    gender = Column("gender", String(length=20), nullable=False, comment="生理性别")
    birthdate = Column("birthdate", Date, comment="出生日期")
    education = Column("education", String(length=50), comment="受教育水平")
    occupation = Column("occupation", String(length=50), comment="职业")
    marriage_status = Column("marriage_status", String(length=20), comment="婚姻状态")
    abo_blood_type = Column("abo_blood_type", String(length=20), comment="ABO血型")
    left_hand_flag = Column("left_hand_flag", String(length=20), comment="是否为左撇子")
    death_date = Column("death_date", Date, comment="死亡日期")
    cellphone_number = Column("cellphone_number", String(length=50), comment="手机号码")
    email = Column("email", String(length=255), comment="联系邮箱")
    address = Column("address", String(length=255), comment="住址")
    gmt_create = Column(
        "gmt_create",
        TIMESTAMP,
        nullable=False,
        server_default=func.utcnow(),
        comment="创建时间(UTC)",
    )
    gmt_modified = Column(
        "gmt_modified",
        TIMESTAMP,
        nullable=False,
        server_default=func.utcnow(),
        onupdate=func.utcnow(),
        comment="最近修改时间(UTC)",
    )
    is_deleted = Column(
        "is_deleted",
        Boolean,
        nullable=False,
        server_default=expression.false(),
        comment="记录是否被删除",
    )

    def __repr__(self):
        return (
            f"SubjectHuman(id={self.id!r},subject_id={self.subject_id!r},gender={self.gender!r},"
            f"birthdate={self.birthdate!r},education={self.education!r},occupation={self.occupation!r},"
            f"marriage_status={self.marriage_status!r},abo_blood_type={self.abo_blood_type!r},"
            f"left_hand_flag={self.left_hand_flag!r},death_date={self.death_date!r},"
            f"cellphone_number={self.cellphone_number!r},email={self.email!r},address={self.address!r},"
            f"gmt_create={self.gmt_create!r},gmt_modified={self.gmt_modified!r},is_deleted={self.is_deleted!r})"
        )


class SubjectAnimal(Base):
    __tablename__ = "subject_animal"

    id = Column("id", BigInteger, primary_key=True, comment="主键")
    animal_subject_id = Column(
        "animal_subject_id",
        String(length=255),
        nullable=False,
        unique=True,
        index=True,
        comment="实验对象的唯一识别编号，系统自动生成",
    )
    species = Column("species", String(length=20), nullable=False, comment="物种")
    gender = Column("gender", String(length=20), nullable=False, comment="生理性别")
    purchase_date = Column("purchase_date", Date, nullable=False, comment="购买日期")
    birthdate = Column("birthdate", Date, comment="出生日期")
    death_date = Column("death_date", Date, comment="死亡日期")
    gmt_create = Column(
        "gmt_create",
        TIMESTAMP,
        nullable=False,
        server_default=func.utcnow(),
        comment="创建时间(UTC)",
    )
    gmt_modified = Column(
        "gmt_modified",
        TIMESTAMP,
        nullable=False,
        server_default=func.utcnow(),
        onupdate=func.utcnow(),
        comment="最近修改时间(UTC)",
    )
    is_deleted = Column(
        "is_deleted",
        Boolean,
        nullable=False,
        server_default=expression.false(),
        comment="记录是否被删除",
    )

    def __repr__(self):
        return (
            f"SubjectAnimal(id={self.id!r},animal_subject_id={self.animal_subject_id!r},species={self.species!r},"
            f"gender={self.gender!r},purchase_date={self.purchase_date!r},birthdate={self.birthdate!r},"
            f"death_date={self.death_date!r},gmt_create={self.gmt_create!r},gmt_modified={self.gmt_modified!r},"
            f"is_deleted={self.is_deleted!r})"
        )
