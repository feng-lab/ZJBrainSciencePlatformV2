import logging
from typing import Any, TypeVar

from sqlalchemy import insert, select
from sqlalchemy.engine import CursorResult
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.db import Base

logger = logging.getLogger(__name__)

OrmModel = TypeVar("OrmModel", bound=Base)


def insert_table(
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


def bulk_insert_table(
    db: Session, table: type[OrmModel], rows: list[dict[str, Any]], *, commit: bool
) -> bool:
    if len(rows) < 1:
        return True
    success = False
    try:
        stmt = insert(table).values(rows)
        result: CursorResult = db.execute(stmt)
        if result.rowcount != len(rows):
            return False
        success = True
        return True
    except DBAPIError as e:
        logger.error(f"insert table {table.__name__} error, msg='{e.detail}', values={rows}")
        return False
    finally:
        if not success:
            db.rollback()
        elif commit:
            db.commit()


def get_deleted_rows(db: Session, table: type[OrmModel], ids: list[int]) -> list[int] | None:
    if len(ids) < 1:
        return []
    try:
        stmt = select(table.id).where(table.id.in_(list(set(ids))), table.is_deleted == True)
        return db.execute(stmt).scalars().all()
    except DBAPIError as e:
        logger.error(f"select deleted rows in {table.__name__} error, {ids=}, msg={e}")
        return None
