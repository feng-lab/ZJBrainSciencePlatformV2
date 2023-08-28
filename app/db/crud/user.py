from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.common.exception import ServiceError
from app.db import common_crud
from app.db.crud import query_pages
from app.db.orm import User
from app.model.schema import UserAuth, UserCreate, UserSearch


def search_users(db: Session, search: UserSearch) -> tuple[int, Sequence[User]]:
    stmt = select(User)
    if search.username:
        stmt = stmt.where(User.username.icontains(search.username))
    if search.staff_id:
        stmt = stmt.where(User.staff_id.icontains(search.staff_id))
    if search.access_level is not None:
        stmt = stmt.where(User.access_level == search.access_level)
    if not search.include_deleted:
        stmt = stmt.where(User.is_deleted == False)
    return query_pages(db, stmt, search.offset, search.limit)


def get_user_access_level(db: Session, user_id: int) -> int | None:
    return db.execute(select(User.access_level).where(User.id == user_id, User.is_deleted == False)).scalar()


def get_user_auth_by_staff_id(db: Session, staff_id: str) -> UserAuth | None:
    stmt = select(User.id, User.username, User.staff_id, User.access_level, User.hashed_password).where(
        User.staff_id == staff_id, User.is_deleted == False
    )
    row = db.execute(stmt).first()
    return UserAuth.from_orm(row) if row is not None else None


def insert_or_update_user(db: Session, user: UserCreate) -> None:
    user_id = db.execute(select(User.id).where(User.username == user.username, User.staff_id == user.staff_id)).scalar()
    if user_id is None:
        if common_crud.insert_row(db, User, user.dict(), commit=True) is None:
            raise ServiceError.database_fail()
    else:
        if not common_crud.update_row(db, User, user.dict() | {"is_deleted": False}, id_=user_id, commit=True):
            raise ServiceError.database_fail()


def get_user_staff_id(db: Session, user_id: int) -> str | None:
    return db.execute(select(User.staff_id).where(User.id == user_id, User.is_deleted == False)).scalar()


def load_user_info(load):
    return load.load_only(User.id, User.username, User.staff_id)
