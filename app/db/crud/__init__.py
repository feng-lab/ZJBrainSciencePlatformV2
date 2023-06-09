import logging
from typing import Any, Sequence

from sqlalchemy import Select, func, select, text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def query_pages(
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
