from sqlalchemy import Column, String, DateTime, Integer

from app.database import Base


class LoginMaster(Base):
    __tablename__ = "login_master"

    uid = Column("Uid", Integer, primary_key=True, comment="主键")
    user_account = Column(
        "UserAccount", String(length=255), nullable=False, comment="用户名"
    )
    password = Column("Password", String(length=255), nullable=False, comment="密码")
    staff_id = Column("StaffID", String(length=255), nullable=False, comment="员工号")
    account_type = Column(
        "AccountType", String(length=255), nullable=False, comment="账户类别"
    )
    create_datetime = Column("CreateDatetime", DateTime, nullable=False, comment="创建时间")
    last_login_datetime = Column(
        "LastLoginDatetime", DateTime, nullable=True, comment="上次登录时间"
    )
    last_logout_datetime = Column(
        "LastLogoutDatetime", DateTime, nullable=True, comment="上次下线时间"
    )

    def __repr__(self):
        return (
            f"LoginMaster(uid={self.uid!r},user_account={self.user_account!r},password={self.password!r},"
            f"staff_id={self.staff_id!r},account_type={self.account_type!r},create_datetime={self.create_datetime!r},"
            f"last_login_datetime={self.last_login_datetime!r},last_logout_datetime={self.last_logout_datetime!r})"
        )


class StaffMaster(Base):
    __tablename__ = "staff_master"

    uid = Column("Uid", Integer, primary_key=True, comment="主键")
    staff_id = Column("StaffID", String(length=255), nullable=False, comment="员工号")
    staff_name = Column("Staff", String(length=255), nullable=False, comment="人员名称")
    staff_type = Column("StaffType", String(length=255), nullable=False, comment="人员类别")
    staff_status = Column(
        "StaffStatus", String(length=20), nullable=False, comment="员工状态，在职或离职"
    )
    institution = Column(
        "Institution", String(length=255), nullable=False, comment="所属机构"
    )
    creator_id = Column(
        "CreatorID", String(length=255), nullable=False, comment="创建人编号，若为自己创建，则为0"
    )
    create_datetime = Column("CreateDatetime", DateTime, nullable=False, comment="人员类别")
    email = Column("Email", String(length=255), comment="联系邮箱")
    cellphone_number = Column("CellphoneNumber", String(length=255), comment="手机号码")

    def __repr__(self):
        return (
            f"StaffMaster(uid={self.uid!r},staff_id={self.staff_id!r},staff_name={self.staff_name!r},"
            f"staff_type={self.staff_type!r},staff_status={self.staff_status!r},institution={self.institution!r},"
            f"creator_id={self.creator_id!r},create_datetime={self.create_datetime!r},email={self.email!r},"
            f"cellphone_number={self.cellphone_number!r})"
        )
