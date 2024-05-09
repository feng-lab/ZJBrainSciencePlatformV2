from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.crud import query_pages
from app.db.orm import Species
from app.model.schema import SpeciesSearch


def search_species(db: Session, search: SpeciesSearch) -> tuple[int, Sequence[Species]]:
    base_stmt = select(Species).select_from(Species)

    if search.chinese_name is not None:
        base_stmt = base_stmt.where(Species.chinese_name.icontains(search.chinese_name))
    if search.english_name is not None:
        base_stmt = base_stmt.where(Species.english_name.icontains(search.english_name))
    if search.latin_name is not None:
        base_stmt = base_stmt.where(Species.english_name.icontains(search.latin_name))
    if not search.include_deleted:
        base_stmt = base_stmt.where(Species.is_deleted == False)
    return query_pages(db, base_stmt, search.offset, search.limit)
