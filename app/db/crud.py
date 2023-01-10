import logging
from datetime import datetime
from typing import Any, Callable

from sqlalchemy import func, insert, select, text, update
from sqlalchemy.engine import CursorResult, Row
from sqlalchemy.orm import Session
from sqlalchemy.sql.roles import OrderByRole, WhereHavingRole

from app.common.config import config
from app.common.util import Model, T, now
from app.db.common_crud import OrmModel
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
    ExperimentResponse,
    FileInDB,
    FileResponse,
    NotificationInDB,
    NotificationResponse,
    ParadigmInDB,
    ParadigmResponse,
    UserAuth,
    UserCreate,
    UserIdNameStaffId,
    UserInDB,
    UserResponse,
)

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

    def page_param(self, page_param: GetModelsByPageParam) -> "SearchModel":
        self.offset = page_param.offset
        self.limit = page_param.limit
        if not page_param.include_deleted:
            self.where.append(self.table.is_deleted == False)
        return self

    def order_by(self, order_by: OrderByRole) -> "SearchModel":
        self.order = order_by
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
        stmt = select(columns).where(*self.where)
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
    result: CursorResult = db.execute(insert(table).values(**model.dict()))
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


def get_user_auth_by_username(db: Session, username: str) -> UserAuth | None:
    stmt = select(
        User.id, User.username, User.staff_id, User.access_level, User.hashed_password
    ).where(User.username == username, User.is_deleted == False)
    row = db.execute(stmt).one_or_none()
    return UserAuth.from_orm(row) if row is not None else None


def search_users(
    db: Session,
    username: str | None,
    staff_id: str | None,
    access_level: int | None,
    page_param: GetModelsByPageParam,
) -> PagedData[UserResponse]:
    return (
        SearchModel(db, User)
        .where_contains(User.username, username)
        .where_contains(User.staff_id, staff_id)
        .where_eq(User.access_level, access_level)
        .page_param(page_param)
        .map_model_with(lambda row: UserResponse(**UserInDB.from_orm(row[0]).dict()))
        .paged_data(UserResponse)
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


def get_notification_unread_count(db: Session, user_id: int) -> int:
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
    page_param: GetModelsByPageParam,
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
    db: Session, user_id: int, status: Notification.Status | None, page_param: GetModelsByPageParam
) -> list[NotificationResponse]:
    return (
        build_search_notification(db)
        .page_param(page_param)
        .where_eq(Notification.receiver, user_id)
        .where_eq(Notification.status, status)
        .order_by(Notification.gmt_create.desc())
        .items(NotificationResponse)
    )


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


def search_files(
    db: Session, experiment_id: int, name: str, extension: str, page_param: GetModelsByPageParam
) -> PagedData[FileResponse]:
    def map_model(row: Row) -> FileResponse:
        file = FileResponse(**FileInDB.from_orm(row[0]).dict())
        if file.extension in config.IMAGE_FILE_EXTENSIONS:
            file.url = f"/api/downloadFile/{file.id}"
        return file

    return (
        SearchModel(db, File)
        .where_eq(File.experiment_id, experiment_id)
        .where_contains(File.name, name)
        .where_contains(File.extension, extension)
        .page_param(page_param)
        .order_by(File.index.asc())
        .map_model_with(map_model)
        .paged_data(FileResponse)
    )


def get_experiment_by_id(db: Session, experiment_id: int) -> ExperimentResponse | None:
    stmt = (
        select(Experiment, User.username, User.staff_id)
        .select_from(Experiment)
        .outerjoin(User, Experiment.main_operator == User.id)
        .where(
            Experiment.id == experiment_id, Experiment.is_deleted == False, User.is_deleted == False
        )
        .limit(1)
    )
    row = db.execute(stmt).first()
    if row is None:
        return None
    experiment_in_db = ExperimentInDB.from_orm(row[0])
    experiment = ExperimentResponse(
        main_operator=UserIdNameStaffId(
            id=experiment_in_db.main_operator, username=row[1], staff_id=row[2]
        ),
        assistants=[],
        **experiment_in_db.dict(exclude={"main_operator"}),
    )
    return experiment


def list_experiment_assistants(db: Session, experiment_id: int) -> list[UserIdNameStaffId]:
    stmt = (
        select(User.id, User.username, User.staff_id)
        .select_from(ExperimentAssistant)
        .outerjoin(User, ExperimentAssistant.user_id == User.id)
        .where(
            ExperimentAssistant.experiment_id == experiment_id,
            ExperimentAssistant.is_deleted == False,
            User.is_deleted == False,
        )
    )
    rows = db.execute(stmt).all()
    return [UserIdNameStaffId(id=row[0], username=row[1], staff_id=row[2]) for row in rows]


def search_experiments(
    db: Session,
    search: str,
    sort_by: GetExperimentsByPageSortBy,
    sort_order: GetExperimentsByPageSortOrder,
    page_param: GetModelsByPageParam,
) -> list[ExperimentResponse]:
    if sort_by is GetExperimentsByPageSortBy.START_TIME:
        column = Experiment.start_at
    elif sort_by is GetExperimentsByPageSortBy.TYPE:
        column = Experiment.type
    else:
        raise ValueError("invalid sort_by")
    if sort_order is GetExperimentsByPageSortOrder.ASC:
        sort_by_spec = column.asc()
    elif sort_order is GetExperimentsByPageSortOrder.DESC:
        sort_by_spec = column.desc()
    else:
        raise ValueError("invalid sort_order")
    return (
        SearchModel(db, Experiment)
        .select(Experiment, User.username, User.staff_id)
        .join(User, Experiment.main_operator == User.id, is_outer=True)
        .where_contains(Experiment.name, search)
        .page_param(page_param)
        .order_by(sort_by_spec)
        .map_model_with(
            lambda row: ExperimentResponse(
                main_operator=UserIdNameStaffId(
                    id=row[0].main_operator, username=row[1], staff_id=row[2]
                ),
                assistants=[],
                **ExperimentInDB.from_orm(row[0]).dict(exclude={"main_operator"}),
            )
        )
        .items(ExperimentResponse)
    )


def bulk_list_experiment_assistants(
    db: Session, experiment_ids: list[int]
) -> list[list[UserIdNameStaffId]]:
    return [list_experiment_assistants(db, experiment_id) for experiment_id in experiment_ids]


def search_experiment_assistants(
    db: Session, experiment_id: int, assistant_ids: list[int]
) -> list[int]:
    stmt = select(ExperimentAssistant.user_id).where(
        ExperimentAssistant.experiment_id == experiment_id,
        ExperimentAssistant.user_id.in_(assistant_ids),
        ExperimentAssistant.is_deleted == False,
    )
    return db.execute(stmt).scalars().all()


def get_paradigm_by_id(db: Session, paradigm_id: int) -> ParadigmResponse | None:
    stmt = (
        select(Paradigm, User.username, User.staff_id)
        .select_from(Paradigm)
        .outerjoin(User, Paradigm.creator == User.id)
        .where(Paradigm.id == paradigm_id, Paradigm.is_deleted == False, User.is_deleted == False)
        .limit(1)
    )
    row = db.execute(stmt).first()
    if row is None:
        return None
    return ParadigmResponse(
        creator=UserIdNameStaffId(id=row[0].creator, username=row[1], staff_id=row[2]),
        images=[],
        **ParadigmInDB.from_orm(row[0]).dict(exclude={"creator"}),
    )


def list_paradigm_files(db: Session, paradigm_id: int) -> list[int]:
    stmt = select(ParadigmFile.file_id).where(
        ParadigmFile.paradigm_id == paradigm_id, ParadigmFile.is_deleted == False
    )
    return db.execute(stmt).scalars().all()


def search_paradigms(
    db: Session, experiment_id: int, page_param: GetModelsByPageParam
) -> list[ParadigmResponse]:
    return (
        SearchModel(db, Paradigm)
        .select(Paradigm, User.username, User.staff_id)
        .join(User, Paradigm.creator == User.id, is_outer=True)
        .where_eq(Paradigm.experiment_id, experiment_id)
        .page_param(page_param)
        .map_model_with(
            lambda row: ParadigmResponse(
                creator=UserIdNameStaffId(id=row[0].creator, username=row[1], staff_id=row[2]),
                images=[],
                **ParadigmInDB.from_orm(row[0]).dict(exclude={"creator"}),
            )
        )
        .items(ParadigmResponse)
    )


def bulk_list_paradigm_files(db: Session, paradigm_ids: list[int]) -> list[list[int]]:
    return [list_paradigm_files(db, paradigm_id) for paradigm_id in paradigm_ids]
