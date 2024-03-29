from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.crud import query_pages
from app.db.orm import EEGData
from app.model.schema import EEGDataSearch


def search_eegdata(db: Session, search: EEGDataSearch) -> tuple[int, Sequence[EEGData]]:
    base_stmt = select(EEGData).select_from(EEGData)
    if search.user_id is not None:
        base_stmt = base_stmt.where(EEGData.user_id == search.user_id)
    if search.gender is not None:
        base_stmt = base_stmt.where(EEGData.gender == search.gender)
    if search.data_update_year is not None:
        base_stmt = base_stmt.where(EEGData.data_update_year == search.data_update_year)
    if search.age is not None:
        base_stmt = base_stmt.where(EEGData.age.icontains(search.age))
    if not search.include_deleted:
        base_stmt = base_stmt.where(EEGData.is_deleted == False)
    return query_pages(db, base_stmt, search.offset, search.limit)
