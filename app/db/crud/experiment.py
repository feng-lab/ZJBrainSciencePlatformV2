import logging
from typing import Any, Sequence

from sqlalchemy import CursorResult, and_, insert, or_, select, update
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session, immediateload, joinedload, load_only, raiseload, subqueryload

from app.db import common_crud
from app.db.crud import load_user_info
from app.db.orm import Experiment, ExperimentAssistant, ExperimentTag, User
from app.model.request import GetExperimentsByPageSortBy, GetExperimentsByPageSortOrder
from app.model.schema import ExperimentSearch

logger = logging.getLogger(__name__)

SEARCH_EXPERIMENT_SORT_BY_COLUMN = {
    GetExperimentsByPageSortBy.START_TIME: Experiment.start_at,
    GetExperimentsByPageSortBy.TYPE: Experiment.type,
}


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
            insert_result: CursorResult = db.execute(insert(Experiment).values(**row))
            assert insert_result.rowcount == 1
            exists_experiment_id = insert_result.inserted_primary_key.id
        else:
            exists_experiment_id = exists_result.id
        if exists_experiment_id != id_:
            update_result: CursorResult = db.execute(
                update(Experiment)
                .where(Experiment.id == exists_experiment_id)
                .values(id=id_, **row)
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


def get_experiment_by_id(db: Session, experiment_id: int) -> Experiment | None:
    stmt = (
        select(Experiment)
        .where(Experiment.id == experiment_id, Experiment.is_deleted == False)
        .options(
            load_user_info(joinedload(Experiment.main_operator_obj)),
            load_user_info(subqueryload(Experiment.assistants)),
            immediateload(Experiment.tags),
        )
    )
    experiment = db.execute(stmt).scalar()
    return experiment


def search_experiments(db: Session, search: ExperimentSearch) -> Sequence[Experiment]:
    stmt = (
        select(Experiment)
        .where(Experiment.id != 0)
        .offset(search.offset)
        .limit(search.limit)
        .options(raiseload(Experiment.main_operator_obj), raiseload(Experiment.assistants))
    )
    if search.search:
        stmt = stmt.where(Experiment.name.icontains(search.search))
    if not search.include_deleted:
        stmt = stmt.where(Experiment.is_deleted == False)
    order_by_column = SEARCH_EXPERIMENT_SORT_BY_COLUMN[search.sort_by]
    if search.sort_order is GetExperimentsByPageSortOrder.DESC:
        stmt = stmt.order_by(order_by_column.desc())
    else:
        stmt = stmt.order_by(order_by_column.asc())

    experiments = db.execute(stmt).scalars().all()
    return experiments


def list_experiment_assistants(db: Session, experiment_id: int) -> Sequence[User]:
    stmt = (
        select(User)
        .options(load_only(User.id, User.username, User.staff_id))
        .join(Experiment.assistants)
        .where(
            Experiment.id == experiment_id, Experiment.is_deleted == False, User.is_deleted == False
        )
    )
    users = db.execute(stmt).scalars().all()
    return users


def search_experiment_assistants(
    db: Session, experiment_id: int, assistant_ids: list[int]
) -> Sequence[int]:
    stmt = select(ExperimentAssistant.user_id).where(
        ExperimentAssistant.experiment_id == experiment_id,
        ExperimentAssistant.user_id.in_(assistant_ids),
    )
    assistants = db.execute(stmt).scalars().all()
    return assistants


def update_experiment_tags(db: Session, experiment_id: int, new_tags: set[str]) -> bool:
    old_tags = set(
        db.execute(select(ExperimentTag.tag).where(ExperimentTag.experiment_id == experiment_id))
        .scalars()
        .all()
    )
    delete_success = common_crud.bulk_delete_rows(
        db,
        ExperimentTag,
        [ExperimentTag.experiment_id == experiment_id, ExperimentTag.tag.in_(old_tags - new_tags)],
        commit=False,
    )
    insert_success = common_crud.bulk_insert_rows(
        db,
        ExperimentTag,
        [{"experiment_id": experiment_id, "tag": tag} for tag in new_tags - old_tags],
        commit=False,
    )
    return delete_success and insert_success
