from sqlalchemy import Column, String, DateTime, Integer

from app.database import Base


class LoginMaster(Base):
    __tablename__ = "login_master"

    uid = Column("uid", Integer, primary_key=True, comment="主键")
    user_account = Column(
        "user_account", String(length=255), nullable=False, comment="用户名"
    )
    password = Column("password", String(length=255), nullable=False, comment="密码")
    staff_id = Column("staff_id", String(length=255), nullable=False, comment="员工号")
    account_type = Column(
        "account_type", String(length=255), nullable=False, comment="账户类别"
    )
    create_datetime = Column(
        "create_datetime", DateTime, nullable=False, comment="创建时间"
    )
    last_login_datetime = Column(
        "last_login_datetime", DateTime, nullable=True, comment="上次登录时间"
    )
    last_logout_datetime = Column(
        "last_logout_datetime", DateTime, nullable=True, comment="上次下线时间"
    )

    def __repr__(self):
        return (
            f"LoginMaster(uid={self.uid!r},user_account={self.user_account!r},password={self.password!r},"
            f"staff_id={self.staff_id!r},account_type={self.account_type!r},create_datetime={self.create_datetime!r},"
            f"last_login_datetime={self.last_login_datetime!r},last_logout_datetime={self.last_logout_datetime!r})"
        )
