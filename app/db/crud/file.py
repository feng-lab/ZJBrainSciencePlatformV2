from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.crud import query_paged_data
from app.db.orm import File
from app.model.schema import FileSearch


def get_file_extensions(db: Session, experiment_id: int) -> Sequence[str]:
    stmt = (
        select(File.extension)
        .where(
            File.experiment_id == experiment_id,
            File.is_deleted == False,
            File.paradigm_id.is_(None),
        )
        .group_by(File.extension)
    )
    extensions = db.execute(stmt).scalars().all()
    return extensions


def search_files(db: Session, search: FileSearch) -> tuple[int, Sequence[File]]:
    base_stmt = select(File).where(File.paradigm_id.is_(None)).order_by(File.id.asc())
    if search.experiment_id is not None:
        base_stmt = base_stmt.where(File.experiment_id == search.experiment_id)
    if search.name:
        base_stmt = base_stmt.where(File.name.icontains(search.name))
    if search.file_type:
        base_stmt = base_stmt.where(File.extension.icontains(search.file_type))
    if not search.include_deleted:
        base_stmt = base_stmt.where(File.is_deleted == False)

    return query_paged_data(db, base_stmt, search.offset, search.limit)
