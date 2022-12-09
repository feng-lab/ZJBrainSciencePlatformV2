import functools
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, TypeVar

from pydantic import BaseModel
from sqlalchemy import func, insert, select, text, update
from sqlalchemy.engine import CursorResult, Result
from sqlalchemy.orm import Session
from sqlalchemy.sql import Executable
from sqlalchemy.sql.roles import WhereHavingRole

from app.common.time import convert_timezone_after_get_db, convert_timezone_before_save, utc_now
from app.common.util import Model
from app.db.database import Base
from app.db.orm import (
    Experiment,
    ExperimentAssistant,
    File,
    Notification,
    Paradigm,
    ParadigmFile,
    User,
)
from app.model.request import (
    GetExperimentsByPageSortBy,
    GetExperimentsByPageSortOrder,
    GetModelsByPageParam,
)
from app.model.response import PagedData
from app.model.schema import (
    ExperimentInDB,
    FileInDB,
    FileResponse,
    NotificationInDB,
    NotificationResponse,
    ParadigmInDB,
    UserAuth,
    UserCreate,
    UserInDB,
    UserResponse,
)

logger = logging.getLogger(__name__)

OrmModel = TypeVar("OrmModel", bound=Base)
Exec = TypeVar("Exec", bound=Executable)
Res = TypeVar("Res", bound=Result)


def convert_db_model_timezone(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        result = fn(*args, **kwargs)
        if result is None:
            return None
        if isinstance(result, BaseModel):
            return convert_timezone_after_get_db(result)
        if isinstance(result, list):
            return [
                convert_timezone_after_get_db(model) if isinstance(model, BaseModel) else model
                for model in result
            ]
        return result

    return wrapper


@convert_db_model_timezone
def get_model(
    db: Session, table: type[OrmModel], target_model: type[Model], id_: int
) -> Model | None:
    stmt = select(table).where(table.id == id_, table.is_deleted == False)
    row = db.execute(stmt).one_or_none()
    return target_model.from_orm(row[0]) if row is not None else None


def exists_model(db: Session, table: type[OrmModel], id_: int) -> bool:
    stmt = select(text("1")).select_from(table).where(table.id == id_, table.is_deleted == False)
    return db.execute(stmt).scalar() is not None


def insert_model(db: Session, table: type[OrmModel], model: Model) -> int:
    model = convert_timezone_before_save(model)
    result: CursorResult = db.execute(insert(table).values(**model.dict()))
    db.commit()
    return result.inserted_primary_key.id


def bulk_insert_models(db: Session, table: type[OrmModel], models: list[Model]) -> None:
    model_dicts = [convert_timezone_before_save(model).dict() for model in models]
    db.execute(insert(table), model_dicts)
    db.commit()


def update_model(db: Session, table: type[OrmModel], id_: int, **values: Any) -> bool:
    return bulk_update_models(db, table, table.id == id_, **values) > 0


def bulk_update_models(
    db: Session, table: type[OrmModel], *where: WhereHavingRole, **values: Any
) -> int:
    values = values | {"gmt_modified": utc_now()}
    result: CursorResult = db.execute(update(table).where(*where).values(**values))
    db.commit()
    # noinspection PyTypeChecker
    return result.rowcount


def update_model_as_deleted(db: Session, table: type[OrmModel], id_: int) -> bool:
    return update_model(db, table, id_, is_deleted=True)


def bulk_update_models_as_deleted(db: Session, table: type[OrmModel], *where) -> int:
    return bulk_update_models(db, table, *where, is_deleted=True)


def get_user_access_level(db: Session, user_id: int) -> int | None:
    return db.execute(
        select(User.access_level).where(User.id == user_id, User.is_deleted == False)
    ).scalar()


@convert_db_model_timezone
def get_user_auth_by_username(db: Session, username: str) -> UserAuth | None:
    stmt = select(
        User.id, User.username, User.staff_id, User.access_level, User.hashed_password
    ).where(User.username == username, User.is_deleted == False)
    row = db.execute(stmt).one_or_none()
    return UserAuth.from_orm(row) if row is not None else None


@convert_db_model_timezone
def search_users(
    db: Session,
    username: str | None,
    staff_id: str | None,
    access_level: int | None,
    page_param: GetModelsByPageParam,
) -> PagedData[UserResponse]:
    where = []
    if username:
        where.append(User.username.ilike(f"%{username}%"))
    if staff_id:
        where.append(User.staff_id.ilike(f"%{staff_id}%"))
    if access_level is not None:
        where.append(User.access_level == access_level)
    if not page_param.include_deleted:
        where.append(User.is_deleted == False)
    total_count = db.execute(select(func.count()).select_from(User).where(*where)).scalar()
    users = db.execute(
        select(User).where(*where).offset(page_param.offset).limit(page_param.limit)
    ).scalars()
    return PagedData[UserResponse](
        total=total_count, items=[UserResponse(**UserInDB.from_orm(user).dict()) for user in users]
    )


def insert_or_update_user(db: Session, user: UserCreate) -> None:
    user_id = db.execute(select(User.id).where(User.username == user.username)).scalar()
    if user_id is None:
        insert_model(db, User, user)
    else:
        update_model(db, User, user_id, **user.dict())


def get_user_username(db: Session, user_id: int) -> str | None:
    return db.execute(
        select(User.username).where(User.id == user_id, User.is_deleted == False)
    ).scalar()


@convert_db_model_timezone
def search_notifications(
    db: Session, user_id: int, status: Notification.Status | None, page_param: GetModelsByPageParam
) -> PagedData[NotificationResponse]:
    stmt = select(func.count()).select_from(Notification).where(Notification.receiver == user_id)
    if not page_param.include_deleted:
        stmt = stmt.where(Notification.is_deleted == False)
    if status is not None:
        stmt = stmt.where(Notification.status == status)
    total = db.execute(stmt).scalar()
    responses = list_notifications(db, user_id, status, page_param)
    return PagedData(total=total, items=responses)


@convert_db_model_timezone
def list_notifications(
    db: Session, user_id: int, status: Notification.Status | None, page_param: GetModelsByPageParam
) -> list[NotificationResponse]:
    stmt = (
        select(Notification, User.username)
        .join(User, Notification.creator == User.id)
        .where(Notification.receiver == user_id)
        .offset(page_param.offset)
        .limit(page_param.limit)
        .order_by(Notification.gmt_create.desc())
    )
    if not page_param.include_deleted:
        stmt = stmt.where(Notification.is_deleted == False)
    if status is not None:
        stmt = stmt.where(Notification.status == status)
    rows = db.execute(stmt).all()
    return [
        NotificationResponse(**NotificationInDB.from_orm(row[0]).dict(), creator_name=row[1])
        for row in rows
    ]


def update_notifications_as_read(
    db: Session, user_id: int, is_all: bool, msg_ids: list[int]
) -> None:
    stmt = (
        update(Notification)
        .where(
            Notification.receiver == user_id,
            Notification.is_deleted == False,
            Notification.status == Notification.Status.unread,
        )
        .values(status=Notification.Status.read)
    )
    if not is_all:
        stmt = stmt.where(Notification.id.in_(msg_ids))
    db.execute(stmt)
    db.commit()


def list_unread_notifications(
    db: Session, user_id: int, is_all: bool, msg_ids: list[int]
) -> list[int]:
    stmt = select(Notification.id).where(
        Notification.receiver == user_id,
        Notification.is_deleted == False,
        Notification.status == Notification.Status.unread,
    )
    if not is_all:
        stmt = stmt.where(Notification.id.in_(msg_ids))
    unread_notification_ids = db.execute(stmt).scalars().all()
    return unread_notification_ids


def get_file_last_index(db: Session, experiment_id: int) -> int | None:
    stmt = (
        select(File.index)
        .where(File.experiment_id == experiment_id, File.is_deleted == False)
        .order_by(File.index.desc())
        .limit(1)
    )
    return db.execute(stmt).scalar()


def get_file_extensions(db: Session, experiment_id: int) -> list[str]:
    stmt = (
        select(File.extension)
        .where(File.experiment_id == experiment_id, File.is_deleted == False)
        .group_by(File.extension)
    )
    return db.execute(stmt).scalars().all()


@convert_db_model_timezone
def search_files(
    db: Session, experiment_id: int, path: str, extension: str, page_param: GetModelsByPageParam
) -> PagedData[FileResponse]:
    where = [File.experiment_id == experiment_id]
    if path:
        where.append(File.path.ilike(f"%{path}%"))
    if extension:
        where.append(File.extension.ilike(f"%{extension}%"))
    if not page_param.include_deleted:
        where.append(File.is_deleted == False)
    total = db.execute(select(func.count()).select_from(File).where(*where)).scalar()
    files_stmt = (
        select(File)
        .where(*where)
        .offset(page_param.offset)
        .limit(page_param.limit)
        .order_by(File.index)
    )
    files = db.execute(files_stmt).scalars().all()
    return PagedData(
        total=total, items=[FileResponse(**FileInDB.from_orm(file).dict()) for file in files]
    )


def list_experiment_assistants(db: Session, experiment_id: int) -> list[int]:
    stmt = select(ExperimentAssistant.user_id).where(
        ExperimentAssistant.experiment_id == experiment_id, ExperimentAssistant.is_deleted == False
    )
    return db.execute(stmt).scalars().all()


@convert_db_model_timezone
def search_experiments(
    db: Session,
    search: str,
    sort_by: GetExperimentsByPageSortBy,
    sort_order: GetExperimentsByPageSortOrder,
    page_param: GetModelsByPageParam,
) -> list[ExperimentInDB]:
    stmt = select(Experiment)
    if search:
        stmt = stmt.where(Experiment.name.ilike(f"%{search}%"))
    if not page_param.include_deleted:
        stmt = stmt.where(Experiment.is_deleted == False)
    if sort_by is GetExperimentsByPageSortBy.START_TIME:
        column = Experiment.start_at
    elif sort_by is GetExperimentsByPageSortBy.TYPE:
        column = Experiment.type
    else:
        raise ValueError("invalid sort_by")
    if sort_order is GetExperimentsByPageSortOrder.ASC:
        stmt = stmt.order_by(column.asc())
    elif sort_order is GetExperimentsByPageSortOrder.DESC:
        stmt = stmt.order_by(column.desc())
    else:
        raise ValueError("invalid sort_order")
    rows = db.execute(stmt).scalars().all()
    return [ExperimentInDB.from_orm(row) for row in rows]


def bulk_list_experiment_assistants(db: Session, experiment_ids: list[int]) -> list[list[int]]:
    with ThreadPoolExecutor() as executor:
        return list(
            executor.map(
                lambda experiment_id: list_experiment_assistants(db, experiment_id), experiment_ids
            )
        )


def list_paradigm_files(db: Session, paradigm_id: int) -> list[int]:
    stmt = select(ParadigmFile.id).where(
        ParadigmFile.paradigm_id == paradigm_id, ParadigmFile.is_deleted == False
    )
    return db.execute(stmt).scalars().all()


@convert_db_model_timezone
def search_paradigms(
    db: Session, experiment_id: int, page_param: GetModelsByPageParam
) -> list[ParadigmInDB]:
    stmt = (
        select(Paradigm)
        .where(Paradigm.experiment_id == experiment_id)
        .offset(page_param.offset)
        .limit(page_param.limit)
    )
    if not page_param.include_deleted:
        stmt = stmt.where(Paradigm.is_deleted == False)
    rows = db.execute(stmt).scalars().all()
    return [ParadigmInDB.from_orm(row) for row in rows]


def bulk_list_paradigm_files(db: Session, paradigm_ids: list[int]) -> list[list[int]]:
    with ThreadPoolExecutor() as executor:
        return list(
            executor.map(lambda paradigm_id: list_paradigm_files(db, paradigm_id), paradigm_ids)
        )
