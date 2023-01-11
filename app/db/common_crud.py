import logging
from typing import Any, TypeVar

from sqlalchemy import insert, select, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session
from sqlalchemy.sql.roles import WhereHavingRole

from app.common.util import now
from app.db import Base

logger = logging.getLogger(__name__)

OrmModel = TypeVar("OrmModel", bound=Base)


def insert_row(
    db: Session, table: type[OrmModel], row: dict[str, Any], *, commit: bool
) -> int | None:
    success = False
    try:
        stmt = insert(table).values(row)
        result: CursorResult = db.execute(stmt)
        if result.rowcount != 1:
            return None
        success = True
        return result.inserted_primary_key.id
    except DBAPIError as e:
        logger.error(f"insert table {table.__name__} error, msg={e}")
        return None
    finally:
        if not success:
            db.rollback()
        elif commit:
            db.commit()


def bulk_insert_rows(
    db: Session, table: type[OrmModel], rows: list[dict[str, Any]], *, commit: bool
) -> bool:
    if not rows:
        return True

    success = False
    try:
        stmt = insert(table).values(rows)
        result: CursorResult = db.execute(stmt)
        if result.rowcount == len(rows):
            success = True
    except DBAPIError as e:
        logger.error(f"insert table {table.__name__} error, msg={e}, values={rows}")
    finally:
        if not success:
            db.rollback()
        elif commit:
            db.commit()
    return success


def get_deleted_rows(db: Session, table: type[OrmModel], ids: list[int]) -> list[int] | None:
    if len(ids) < 1:
        return []
    try:
        stmt = select(table.id).where(table.id.in_(list(set(ids))), table.is_deleted == True)
        return db.execute(stmt).scalars().all()
    except DBAPIError as e:
        logger.error(f"select deleted rows in {table.__name__} error, {ids=}, msg={e}")
        return None


def update_row(
    db: Session,
    table: type[OrmModel],
    id_: int,
    update_dict: dict[str, Any],
    *,
    commit: bool,
    touch: bool = True,
) -> bool:
    return bulk_update_rows(db, table, [table.id == id_], update_dict, commit=commit)


def update_row_as_deleted(
    db: Session, table: type[OrmModel], id_: int, *, commit: bool, touch: bool = True
) -> bool:
    return update_row(db, table, id_, {"is_deleted": True}, commit=commit)


def bulk_update_rows(
    db: Session,
    table: type[OrmModel],
    where: list[WhereHavingRole],
    update_dict: dict[str, Any],
    *,
    commit: bool,
    touch: bool = True,
) -> bool:
    success = False
    if touch:
        update_dict = update_dict | {"gmt_modified": now()}
    try:
        stmt = update(table).where(*where).values(**update_dict)
        db.execute(stmt)
        success = True
    except DBAPIError as e:
        logger.error(f"update table {table.__name__} error, msg={e}")
    finally:
        if not success:
            db.rollback()
        elif commit:
            db.commit()
    return success


def bulk_update_rows_as_deleted(
    db: Session, table: type[OrmModel], ids: list[int], *, commit: bool, touch: bool = True
) -> bool:
    return bulk_update_rows(db, table, [table.id.in_(ids)], {"is_deleted": True}, commit=commit)
