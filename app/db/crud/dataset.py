from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.crud import query_pages
from app.db.orm import Dataset
from app.model.schema import DatasetSearch


def search_datasets(db: Session, search: DatasetSearch) -> tuple[int, Sequence[Dataset]]:
    base_stmt = select(Dataset).select_from(Dataset)
    if search.user_id is not None:
        base_stmt = base_stmt.where(Dataset.user_id == search.user_id)
    if search.data_publisher is not None:
        base_stmt = base_stmt.where(Dataset.data_publisher.icontains(search.data_publisher))
    if search.data_update_year is not None:
        base_stmt = base_stmt.where(Dataset.data_update_year == search.data_update_year)
    if search.experiment_platform is not None:
        base_stmt = base_stmt.where(Dataset.experiment_platform.icontains(search.experiment_platform))
    if search.project is not None:
        base_stmt = base_stmt.where(Dataset.project.icontains(search.project))
    if not search.include_deleted:
        base_stmt = base_stmt.where(Dataset.is_deleted == False)
    return query_pages(db, base_stmt, search.offset, search.limit)
