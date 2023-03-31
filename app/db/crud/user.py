from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.crud import SearchModel, insert_model, update_model
from app.db.orm import User
from app.model.response import Page
from app.model.schema import PageParm, UserAuth, UserCreate, UserResponse


def search_users(
    db: Session,
    username: str | None,
    staff_id: str | None,
    access_level: int | None,
    page_param: PageParm,
) -> Page[UserResponse]:
    return (
        SearchModel(db, User)
        .where_contains(User.username, username)
        .where_contains(User.staff_id, staff_id)
        .where_eq(User.access_level, access_level)
        .page_param(page_param)
        .map_model_with(lambda row: UserResponse.from_orm(row[0]))
        .paged_data(UserResponse)
    )


def get_user_access_level(db: Session, user_id: int) -> int | None:
    return db.execute(
        select(User.access_level).where(User.id == user_id, User.is_deleted == False)
    ).scalar()


def get_user_auth_by_staff_id(db: Session, staff_id: str) -> UserAuth | None:
    stmt = select(
        User.id, User.username, User.staff_id, User.access_level, User.hashed_password
    ).where(User.staff_id == staff_id, User.is_deleted == False)
    row = db.execute(stmt).first()
    return UserAuth.from_orm(row) if row is not None else None


def insert_or_update_user(db: Session, user: UserCreate) -> None:
    user_id = db.execute(select(User.id).where(User.username == user.username)).scalar()
    if user_id is None:
        insert_model(db, User, user)
    else:
        update_model(db, User, user_id, **user.dict(), is_deleted=False)


def get_user_staff_id(db: Session, user_id: int) -> str | None:
    return db.execute(
        select(User.staff_id).where(User.id == user_id, User.is_deleted == False)
    ).scalar()