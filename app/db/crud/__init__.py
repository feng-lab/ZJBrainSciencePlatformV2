import logging
import sys
from datetime import datetime
from typing import Any, Callable, Sequence, cast

from sqlalchemy import Select, and_, func, insert, or_, select, text, update
from sqlalchemy.engine import CursorResult, Row
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session, joinedload, load_only, subqueryload
from sqlalchemy.sql.roles import OrderByRole, WhereHavingRole

from app.common.config import config
from app.common.util import Model, T, now
from app.db import OrmModel, common_crud
from app.db.orm import (
    Experiment,
    ExperimentAssistant,
    ExperimentHumanSubject,
    File,
    HumanSubject,
    HumanSubjectIndex,
    Notification,
    Paradigm,
    User,
)
from app.model.request import GetExperimentsByPageSortBy, GetExperimentsByPageSortOrder
from app.model.response import PagedData
from app.model.schema import (
    FileInDB,
    FileResponse,
    HumanSubjectSearch,
    NotificationInDB,
    NotificationResponse,
    PageParm,
    UserAuth,
    UserCreate,
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
        columns = self.columns if self.columns else self.table
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


def get_user_access_level(db: Session, user_id: int) -> int | None:
    return db.execute(
        select(User.access_level).where(User.id == user_id, User.is_deleted == False)
    ).scalar()


def get_user_auth_by_username(db: Session, username: str) -> UserAuth | None:
    stmt = select(
        User.id, User.username, User.staff_id, User.access_level, User.hashed_password
    ).where(User.username == username, User.is_deleted == False)
    row = db.execute(stmt).first()
    return UserAuth.from_orm(row) if row is not None else None


def search_users(
    db: Session,
    username: str | None,
    staff_id: str | None,
    access_level: int | None,
    page_param: PageParm,
) -> PagedData[UserResponse]:
    return (
        SearchModel(db, User)
        .where_contains(User.username, username)
        .where_contains(User.staff_id, staff_id)
        .where_eq(User.access_level, access_level)
        .page_param(page_param)
        .map_model_with(lambda row: UserResponse.from_orm(row[0]))
        .paged_data(UserResponse)
    )


def insert_or_update_user(db: Session, user: UserCreate) -> None:
    user_id = db.execute(select(User.id).where(User.username == user.username)).scalar()
    if user_id is None:
        insert_model(db, User, user)
    else:
        update_model(db, User, user_id, **user.dict(), is_deleted=False)


def get_user_username(db: Session, user_id: int) -> str | None:
    return db.execute(
        select(User.username).where(User.id == user_id, User.is_deleted == False)
    ).scalar()


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
    return list(db.execute(stmt).scalars().all())


def search_files(
    db: Session, experiment_id: int, name: str, extension: str, page_param: PageParm
) -> PagedData[FileResponse]:
    def map_model(row: Row) -> FileResponse:
        file = FileResponse(**FileInDB.from_orm(row[0]).dict())
        if file.extension in config.IMAGE_FILE_EXTENSIONS:
            file.url = f"/api/downloadFile/{file.id}"
        return file

    return (
        SearchModel(db, File)
        .where_eq(File.experiment_id, experiment_id)
        .where_null(File.paradigm_id)
        .where_contains(File.name, name)
        .where_contains(File.extension, extension)
        .page_param(page_param)
        .order_by(File.index.asc())
        .map_model_with(map_model)
        .paged_data(FileResponse)
    )


def insert_or_update_experiment(db: Session, id_: int, row: dict[str, Any]) -> None:
    success = False
    try:
        exists_stmt = (
            select(Experiment.id)
            .where(
                or_(
                    Experiment.id == id_,
                    and_(
                        Experiment.name == row["name"], Experiment.description == row["description"]
                    ),
                )
            )
            .order_by(Experiment.id.asc())
            .limit(1)
        )
        exists_result = db.execute(exists_stmt).first()
        if exists_result is None:
            insert_result = cast(CursorResult, db.execute(insert(Experiment).values(**row)))
            assert insert_result.rowcount == 1
            exists_experiment_id = insert_result.inserted_primary_key.id
        else:
            exists_experiment_id = exists_result.id
        if exists_experiment_id != id_:
            # noinspection PyTypeChecker
            update_result = cast(
                CursorResult,
                db.execute(
                    update(Experiment)
                    .where(Experiment.id == exists_experiment_id)
                    .values(id=id_, **row)
                ),
            )
            assert update_result.rowcount == 1
        success = True
    except DBAPIError as e:
        logger.error(f"insert or update default experiment error, msg={e}")
    finally:
        if success:
            db.commit()
        else:
            db.rollback()


def load_user_info_option(strategy, relation_column):
    return strategy(relation_column).load_only(User.id, User.username, User.staff_id)


def get_experiment_by_id(db: Session, experiment_id: int) -> Experiment | None:
    stmt = (
        select(Experiment)
        .where(Experiment.id == experiment_id, Experiment.is_deleted == False)
        .options(
            load_user_info_option(joinedload, Experiment.main_operator_obj),
            load_user_info_option(subqueryload, Experiment.assistants),
        )
    )
    experiment = db.execute(stmt).scalar()
    return experiment


SEARCH_EXPERIMENT_SORT_BY_COLUMN = {
    GetExperimentsByPageSortBy.START_TIME: Experiment.start_at,
    GetExperimentsByPageSortBy.TYPE: Experiment.type,
}


def search_experiments(
    db: Session,
    search: str,
    sort_by: GetExperimentsByPageSortBy,
    sort_order: GetExperimentsByPageSortOrder,
    page_param: PageParm,
) -> list[Experiment]:
    stmt = (
        select(Experiment)
        .where(Experiment.id != 0)
        .offset(page_param.offset)
        .limit(page_param.limit)
        .options(
            load_user_info_option(joinedload, Experiment.main_operator_obj),
            load_user_info_option(subqueryload, Experiment.assistants),
        )
    )
    if search:
        stmt = stmt.where(Experiment.name.ilike(f"%{search}%"))
    if not page_param.include_deleted:
        stmt = stmt.where(Experiment.is_deleted == False)
    order_by_column = SEARCH_EXPERIMENT_SORT_BY_COLUMN[sort_by]
    if sort_order is GetExperimentsByPageSortOrder.DESC:
        stmt = stmt.order_by(order_by_column.desc())
    else:
        stmt = stmt.order_by(order_by_column.asc())
    experiments = db.execute(stmt).scalars().all()
    return list(experiments)


def list_experiment_assistants(db: Session, experiment_id: int) -> list[User]:
    stmt = (
        select(User.id, User.username, User.staff_id)
        .select_from(ExperimentAssistant)
        .join(
            Experiment,
            and_(
                ExperimentAssistant.experiment_id == Experiment.id, Experiment.is_deleted == False
            ),
        )
        .join(User, and_(ExperimentAssistant.user_id == User.id, User.is_deleted == False))
        .where(ExperimentAssistant.experiment_id == experiment_id)
    )
    users = db.execute(stmt).all()
    # noinspection PyTypeChecker
    return list(users)


def search_experiment_assistants(
    db: Session, experiment_id: int, assistant_ids: list[int]
) -> list[int]:
    stmt = select(ExperimentAssistant.user_id).where(
        ExperimentAssistant.experiment_id == experiment_id,
        ExperimentAssistant.user_id.in_(assistant_ids),
    )
    return list(db.execute(stmt).scalars().all())


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
        .options(load_only(File.id, File.experiment_id, File.index, File.extension))
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


def load_human_subject_user_option():
    return joinedload(HumanSubject.user.and_(User.is_deleted == False), innerjoin=True).load_only(
        User.username, User.staff_id
    )


def get_human_subject(db: Session, user_id: int) -> HumanSubject | None:
    stmt = (
        select(HumanSubject)
        .where(HumanSubject.is_deleted == False, HumanSubject.user_id == user_id)
        .options(load_human_subject_user_option())
    )
    row = db.execute(stmt).scalar()
    return row


def search_human_subjects(db: Session, search: HumanSubjectSearch) -> (int, Sequence[HumanSubject]):
    base_stmt = select(HumanSubject).options(load_human_subject_user_option())
    if search.experiment_id is not None:
        base_stmt = base_stmt.join(
            Experiment.human_subjects.and_(Experiment.is_deleted == False)
        ).where(Experiment.id == search.experiment_id)
    if search.gender is not None:
        base_stmt = base_stmt.where(HumanSubject.gender == search.gender)
    if search.abo_blood_type is not None:
        base_stmt = base_stmt.where(HumanSubject.abo_blood_type == search.abo_blood_type)
    if search.marital_status is not None:
        base_stmt = base_stmt.where(HumanSubject.marital_status == search.marital_status)
    if search.is_left_handed is not None:
        base_stmt = base_stmt.where(HumanSubject.is_left_handed == search.is_left_handed)
    if not search.include_deleted:
        base_stmt = base_stmt.where(HumanSubject.is_deleted == False)

    return query_paged_data(db, base_stmt, search.offset, search.limit)


def query_paged_data(
    db: Session, base_stmt: Select, offset: int, limit: int
) -> tuple[int, Sequence[OrmModel]]:
    items_stmt = base_stmt.offset(offset).limit(limit)
    human_subjects = db.execute(items_stmt).scalars().all()
    total_stmt = base_stmt.with_only_columns(func.count())
    total = db.execute(total_stmt).scalar()
    return total, human_subjects


def list_experiment_human_subjects(db: Session, experiment_id: int) -> Sequence[int]:
    stmt = (
        select(HumanSubject.user_id)
        .join(ExperimentHumanSubject, HumanSubject.user_id == ExperimentHumanSubject.user_id)
        .join(Experiment, ExperimentHumanSubject.experiment_id == Experiment.id)
        .join(User, HumanSubject.user_id == User.id)
        .where(
            ExperimentHumanSubject.experiment_id == experiment_id,
            HumanSubject.is_deleted == False,
            Experiment.is_deleted == False,
            User.is_deleted == False,
        )
    )
    human_subject_user_ids = db.execute(stmt).scalars().all()
    return human_subject_user_ids


def get_next_human_subject_index(
    db: Session, update_index: bool = True, exit_if_update_error: bool = False
) -> int | None:
    next_index: int | None = db.execute(select(HumanSubjectIndex.index)).scalar_one_or_none()
    if next_index is None:
        return None

    if update_index:
        success = common_crud.update_row(
            db,
            HumanSubjectIndex,
            {"index": next_index + 1},
            where=[HumanSubjectIndex.index == next_index],
            commit=True,
            touch=False,
        )
        if not success:
            logger.error(f"update human_subject_index.index error, {next_index=}")
            if exit_if_update_error:
                sys.exit(1)
            else:
                return None

    return next_index


def insert_human_subject_index(db: Session, index: int) -> None:
    common_crud.insert_row(db, HumanSubjectIndex, {"index": index}, commit=True, return_id=False)


def check_human_subject_exists(db: Session, user_id: int) -> bool:
    stmt = (
        select(text("1"))
        .select_from(HumanSubject)
        .join(HumanSubject.user)
        .where(
            HumanSubject.user_id == user_id,
            HumanSubject.is_deleted == False,
            User.is_deleted == False,
        )
    )
    row = db.execute(stmt).first()
    return row is not None
