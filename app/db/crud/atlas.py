from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.crud import query_pages
from app.db.orm import Atlas
from app.model.schema import AtlasSearch


def search_atlases(db: Session, search: AtlasSearch) -> tuple[int, Sequence[Atlas]]:
    base_stmt = select(Atlas).select_from(Atlas)
    if search.name:
        base_stmt = base_stmt.where(Atlas.name.icontains(search.name))
    if not search.include_deleted:
        base_stmt = base_stmt.where(Atlas.is_deleted == False)
    return query_pages(db, base_stmt, search.offset, search.limit)
