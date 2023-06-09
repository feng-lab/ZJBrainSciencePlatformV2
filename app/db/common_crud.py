import logging
from typing import Any, cast

from sqlalchemy import delete, insert, select, text, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session
from sqlalchemy.sql.roles import WhereHavingRole

from app.common.util import now
from app.db import OrmModel

logger = logging.getLogger(__name__)


def get_row_by_id(db: Session, table: type[OrmModel], id_: int) -> OrmModel | None:
    return get_row(db, table, table.id == id_)


def get_row(db: Session, table: type[OrmModel], *where: WhereHavingRole) -> OrmModel | None:
    stmt = select(table).where(table.is_deleted == False, *where)
    row = db.execute(stmt).scalar()
    return row


def exists_row(
    db: Session,
    table: type[OrmModel],
    *,
    id_: int | None = None,
    where: list[WhereHavingRole] | None = None,
    include_deleted: bool = False,
) -> bool:
    if id_ is not None:
        where = [table.id == id_]
    if where is None:
        raise ValueError("neither id_ nor where is provided")
    if not include_deleted:
        where.append(table.is_deleted == False)

    stmt = select(text("1")).select_from(table).where(*where).limit(1)
    row = db.execute(stmt).first()
    return row is not None


def insert_row(
    db: Session, table: type[OrmModel], row: dict[str, Any], *, commit: bool, return_id: bool = True
) -> int | None:
    success = False
    try:
        stmt = insert(table).values(row)
        result: CursorResult = db.execute(stmt)
        if result.rowcount != 1:
            return None
        success = True
        if return_id:
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
        result = cast(CursorResult, db.execute(stmt))
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
        return list(db.execute(stmt).scalars().all())
    except DBAPIError as e:
        logger.error(f"select deleted rows in {table.__name__} error, {ids=}, msg={e}")
        return None


def update_row(
    db: Session,
    table: type[OrmModel],
    update_dict: dict[str, Any],
    *,
    id: int | None = None,
    where: list[WhereHavingRole] | None = None,
    commit: bool,
    touch: bool = True,
) -> bool:
    if id is not None:
        where = [table.id == id]
    if where is None:
        raise ValueError("no id nor where provided")
    return bulk_update_rows(db, table, where, update_dict, commit=commit, touch=touch)


def update_row_as_deleted(
    db: Session,
    table: type[OrmModel],
    *,
    id: int | None = None,
    where: list[WhereHavingRole] | None = None,
    commit: bool,
    touch: bool = True,
) -> bool:
    return update_row(
        db, table, {"is_deleted": True}, id=id, where=where, commit=commit, touch=touch
    )


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
    db: Session,
    table: type[OrmModel],
    *,
    ids: list[int] | None = None,
    where: list[WhereHavingRole] | None = None,
    commit: bool,
    touch: bool = True,
) -> bool:
    if ids is not None:
        where = [table.id.in_(ids)]
    if where is None:
        raise ValueError("no id nor where provided")
    return bulk_update_rows(db, table, where, {"is_deleted": True}, commit=commit, touch=touch)


def bulk_delete_rows(
    db: Session, table: type[OrmModel], where: list[WhereHavingRole], *, commit: bool
) -> bool:
    success = False
    try:
        stmt = delete(table).where(*where)
        db.execute(stmt)
        success = True
    except DBAPIError as e:
        logger.error(f"delete rows from table {table.__name__} error, msg={e}")
    finally:
        if not success:
            db.rollback()
        elif commit:
            db.commit()
    return success
