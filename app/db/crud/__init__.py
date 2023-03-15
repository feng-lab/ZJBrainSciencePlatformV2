import logging
from datetime import datetime
from typing import Any, Callable, Sequence, cast

from sqlalchemy import Select, and_, func, insert, select, text, update
from sqlalchemy.engine import CursorResult, Row
from sqlalchemy.orm import Session, joinedload, load_only, subqueryload
from sqlalchemy.sql.roles import OrderByRole, WhereHavingRole

from app.common.util import Model, T, now
from app.db import OrmModel
from app.db.crud.experiment import load_user_info_option
from app.db.orm import Experiment, File, Notification, Paradigm, User
from app.model.response import PagedData
from app.model.schema import NotificationInDB, NotificationResponse, PageParm

logger = logging.getLogger(__name__)


class SearchModel:
    def __init__(self, db: Session, table: type[OrmModel]):
        self.db: Session = db
        self.table: type[OrmModel] = table
        self.columns: list = []
        self.join_spec: (type[OrmModel], Any, bool) = None
        self.offset: int | None = None
        self.limit: int | None = None
        self.order: OrderByRole | None = None
        self.where: list = []
        self.map_model: Callable[[Row], Model] | None = None

    def select(self, *columns) -> "SearchModel":
        self.columns = columns
        return self

    def join(self, another_table, on_clause, is_outer=False) -> "SearchModel":
        self.join_spec = (another_table, on_clause, is_outer)
        return self

    def page_param(self, page_param: PageParm) -> "SearchModel":
        self.offset = page_param.offset
        self.limit = page_param.limit
        if not page_param.include_deleted:
            self.where.append(self.table.is_deleted == False)
        return self

    def order_by(self, order_by: OrderByRole) -> "SearchModel":
        self.order = order_by
        return self

    def where_null(self, field) -> "SearchModel":
        self.where.append(field.is_(None))
        return self

    def where_eq(self, field, value: T | None) -> "SearchModel":
        if value is not None:
            self.where.append(field == value)
        return self

    def where_contains(self, field, value: str | None) -> "SearchModel":
        if value:
            self.where.append(field.ilike(f"%{value}%"))
        return self

    def where_ge(self, field, value: T | None) -> "SearchModel":
        if value is not None:
            self.where.append(field >= value)
        return self

    def where_le(self, field, value: T | None) -> "SearchModel":
        if value is not None:
            self.where.append(field <= value)
        return self

    def map_model_with(self, map_model: Callable[[Row], Model]) -> "SearchModel":
        self.map_model = map_model
        return self

    def total_count(self) -> int:
        stmt = select(func.count(self.table.id)).where(*self.where)
        if self.join_spec is not None:
            stmt = stmt.join(self.join_spec[0], self.join_spec[1], isouter=self.join_spec[2])
        return self.db.execute(stmt).scalar()

    def items(self, target_model: type[Model]) -> list[Model]:
        columns = self.columns if self.columns else [self.table]
        stmt = select(*columns).where(*self.where)
        if self.join_spec is not None:
            stmt = stmt.join(self.join_spec[0], self.join_spec[1], isouter=self.join_spec[2])
        if self.offset is not None:
            stmt = stmt.offset(self.offset)
        if self.limit is not None:
            stmt = stmt.limit(self.limit)
        if self.order is not None:
            stmt = stmt.order_by(self.order)
        rows = self.db.execute(stmt).all()
        map_model = self.map_model
        if map_model is None:

            def default_map_model(row: Row) -> Model:
                return target_model.from_orm(row[0])

            map_model = default_map_model
        return [map_model(row) for row in rows]

    def paged_data(self, target_model: type[Model]) -> PagedData[Model]:
        total = self.total_count()
        if total < 1:
            items = []
        else:
            items = self.items(target_model)
        return PagedData(total=total, items=items)


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
    result = cast(CursorResult, db.execute(insert(table).values(**model.dict())))
    db.commit()
    return result.inserted_primary_key.id


def bulk_insert_models(db: Session, table: type[OrmModel], models: list[Model]) -> None:
    model_dicts = [model.dict() for model in models]
    db.execute(insert(table), model_dicts)
    db.commit()


def update_model(db: Session, table: type[OrmModel], id_: int, **values: Any) -> bool:
    return bulk_update_models(db, table, table.id == id_, **values) > 0


def bulk_update_models(
    db: Session, table: type[OrmModel], *where: WhereHavingRole, **values: Any
) -> int:
    values = values | {"gmt_modified": now()}
    result = cast(CursorResult, db.execute(update(table).where(*where).values(**values)))
    db.commit()
    # noinspection PyTypeChecker
    return result.rowcount


def update_model_as_deleted(db: Session, table: type[OrmModel], id_: int) -> bool:
    return update_model(db, table, id_, is_deleted=True)


def bulk_update_models_as_deleted(db: Session, table: type[OrmModel], *where) -> int:
    return bulk_update_models(db, table, *where, is_deleted=True)


def get_notification_unread_count(db: Session, user_id: int) -> int:
    # noinspection PyTypeChecker
    stmt = select(func.count(Notification.id)).where(
        Notification.receiver == user_id,
        Notification.status == Notification.Status.unread,
        Notification.is_deleted == False,
    )
    return db.execute(stmt).scalar()


def build_search_notification(db: Session) -> SearchModel:
    return (
        SearchModel(db, Notification)
        .select(Notification, User.username)
        .join(User, Notification.receiver == User.id)
        .map_model_with(
            lambda row: NotificationResponse(
                **NotificationInDB.from_orm(row[0]).dict(), creator_name=row[1]
            )
        )
    )


def search_notifications(
    db: Session,
    user_id: int,
    notification_type: Notification.Type | None,
    status: Notification.Status | None,
    create_time_start: datetime | None,
    create_time_end: datetime | None,
    page_param: PageParm,
) -> PagedData[NotificationResponse]:
    return (
        build_search_notification(db)
        .page_param(page_param)
        .where_eq(Notification.receiver, user_id)
        .where_eq(Notification.type, notification_type)
        .where_eq(Notification.status, status)
        .where_ge(Notification.gmt_create, create_time_start)
        .where_le(Notification.gmt_create, create_time_end)
        .order_by(Notification.gmt_create.desc())
        .paged_data(NotificationResponse)
    )


def list_notifications(
    db: Session, user_id: int, status: Notification.Status | None, page_param: PageParm
) -> list[NotificationResponse]:
    return (
        build_search_notification(db)
        .page_param(page_param)
        .where_eq(Notification.receiver, user_id)
        .where_eq(Notification.status, status)
        .order_by(Notification.gmt_create.desc())
        .items(NotificationResponse)
    )


def list_unread_notifications(
    db: Session, user_id: int, is_all: bool, msg_ids: list[int]
) -> list[int]:
    # noinspection PyTypeChecker
    stmt = select(Notification.id).where(
        Notification.receiver == user_id,
        Notification.is_deleted == False,
        Notification.status == Notification.Status.unread,
    )
    if not is_all:
        stmt = stmt.where(Notification.id.in_(msg_ids))
    unread_notification_ids = db.execute(stmt).scalars().all()
    return list(unread_notification_ids)


def load_paradigm_creator_option():
    return load_user_info_option(joinedload, Paradigm.creator_obj)


def load_paradigm_files_option():
    return subqueryload(Paradigm.files.and_(File.is_deleted == False)).load_only(File.id)


def get_paradigm_by_id(db: Session, paradigm_id: int) -> Paradigm | None:
    stmt = (
        select(Paradigm)
        .where(Paradigm.id == paradigm_id, Paradigm.is_deleted == False)
        .options(load_paradigm_creator_option(), load_paradigm_files_option())
    )
    paradigm = db.execute(stmt).scalar()
    return paradigm


def list_paradigm_files(db: Session, paradigm_id: int) -> list[int]:
    stmt = (
        select(File.id)
        .join(Paradigm.files)
        .where(
            File.paradigm_id == paradigm_id,
            File.is_deleted == False,
            Paradigm.is_deleted == False,
            File.paradigm_id.is_not(None),
        )
    )
    result = db.execute(stmt).scalars().all()
    return list(result)


def list_paradigm_file_infos(db: Session, paradigm_id: int) -> list[File]:
    stmt = (
        select(File)
        .options(load_only(File.id, File.experiment_id, File.extension))
        .join(Paradigm.files)
        .join(
            Experiment,
            and_(Experiment.id == Paradigm.experiment_id, Experiment.is_deleted == False),
        )
        .where(
            File.is_deleted == False,
            Paradigm.is_deleted == False,
            Experiment.is_deleted == False,
            File.paradigm_id.is_not(None),
            Paradigm.id == paradigm_id,
        )
    )
    files = db.execute(stmt).scalars().all()
    return list(files)


def search_paradigms(db: Session, experiment_id: int, page_param: PageParm) -> list[Paradigm]:
    stmt = (
        select(Paradigm)
        .where(Paradigm.experiment_id == experiment_id)
        .join(
            Experiment,
            and_(Paradigm.experiment_id == Experiment.id, Experiment.is_deleted == False),
        )
        .offset(page_param.offset)
        .limit(page_param.limit)
        .options(load_paradigm_creator_option(), load_paradigm_files_option())
    )
    if not page_param.include_deleted:
        stmt = stmt.where(Paradigm.is_deleted == False)
    paradigms = db.execute(stmt).scalars().all()
    return list(paradigms)


def bulk_list_paradigm_files(db: Session, paradigm_ids: list[int]) -> list[list[int]]:
    return [list_paradigm_files(db, paradigm_id) for paradigm_id in paradigm_ids]


def query_paged_data(
    db: Session, base_stmt: Select, offset: int, limit: int, *, scalars: bool = True
) -> tuple[int, Sequence[Any]]:
    items_stmt = base_stmt.offset(offset).limit(limit)
    result = db.execute(items_stmt)
    if scalars:
        result = result.scalars()
    items = result.all()
    total_stmt = base_stmt.with_only_columns(func.count())
    total = db.execute(total_stmt).scalar()
    return total, items


def send_heartbeat(db: Session) -> None:
    db.execute(select(text("1")))
    logger.info("database heartbeat sent")
