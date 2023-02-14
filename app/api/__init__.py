from sqlalchemy.orm import Session
from sqlalchemy.sql.roles import WhereHavingRole

from app.common.exception import ServiceError
from app.db import OrmModel, common_crud, crud
from app.db.orm import Device, Experiment, User


def check_experiment_exists(db: Session, experiment_id: int) -> None:
    return _check_exists(db, Experiment, "实验不存在", id_=experiment_id)


def check_user_exists(db: Session, user_id: int) -> None:
    return _check_exists(db, User, "用户不存在", id_=user_id)


def check_device_exists(db: Session, device_id: int) -> None:
    return _check_exists(db, Device, "设备不存在", id_=device_id)


def check_human_subject_exists(db: Session, user_id: int) -> None:
    if not crud.check_human_subject_exists(db, user_id):
        raise ServiceError.not_found("被试者不存在")


def _check_exists(
    db: Session,
    table: type[OrmModel],
    not_found_msg: str,
    *,
    id_: int | None = None,
    where: list[WhereHavingRole] | None = None,
) -> None:
    exists = common_crud.exists_row(db, table, id_=id_, where=where)
    if not exists:
        raise ServiceError.not_found(not_found_msg)
