from sqlalchemy.orm import Session

from app.common.exception import ServiceError
from app.db import common_crud
from app.db.orm import Experiment


def check_experiment_exists(db: Session, experiment_id: int) -> None:
    return _check_exists(db, experiment_id, "实验不存在")


def check_user_exists(db: Session, user_id: int) -> None:
    return _check_exists(db, user_id, "用户不存在")


def _check_exists(db: Session, id_: int, not_found_msg: str) -> None:
    exists = common_crud.check_row_valid(db, Experiment, id_)
    if exists is None:
        raise ServiceError.database_fail("数据库错误")
    elif not exists:
        raise ServiceError.not_found(not_found_msg)
