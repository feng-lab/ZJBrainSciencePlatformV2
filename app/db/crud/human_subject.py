import logging
import sys
from typing import Sequence

from sqlalchemy import select, text
from sqlalchemy.orm import Session, joinedload

from app.db import common_crud
from app.db.crud import query_paged_data
from app.db.orm import Experiment, ExperimentHumanSubject, HumanSubject, HumanSubjectIndex, User
from app.model.schema import HumanSubjectSearch

logger = logging.getLogger(__name__)


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


def get_human_subject(db: Session, user_id: int) -> HumanSubject | None:
    stmt = (
        select(HumanSubject)
        .where(HumanSubject.is_deleted == False, HumanSubject.user_id == user_id)
        .options(load_human_subject_user_option())
    )
    row = db.execute(stmt).scalar()
    return row


def search_human_subjects(
    db: Session, search: HumanSubjectSearch
) -> tuple[int, Sequence[HumanSubject]]:
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


def load_human_subject_user_option():
    return joinedload(HumanSubject.user.and_(User.is_deleted == False), innerjoin=True).load_only(
        User.username, User.staff_id
    )
