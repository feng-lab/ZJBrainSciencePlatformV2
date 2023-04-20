import logging
from typing import Any, Callable, Sequence

from sqlalchemy import Select, func, select, text
from sqlalchemy.engine import Row
from sqlalchemy.orm import Session
from sqlalchemy.sql.roles import OrderByRole

from app.common.util import Model, T
from app.db import OrmModel
from app.model.response import Page
from app.model.schema import PageParm

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
        columns = self.columns if self.columns else [self.table]
        stmt = select(*columns).where(*self.where)
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

    def paged_data(self, target_model: type[Model]) -> Page[Model]:
        total = self.total_count()
        if total < 1:
            items = []
        else:
            items = self.items(target_model)
        return Page(total=total, items=items)


def query_paged_data(
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
