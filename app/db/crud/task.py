from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, load_only

from app.db.crud import query_paged_data
from app.db.orm import Experiment, File
from app.model.schema import TaskSourceFileSearch


def search_source_files(
    db: Session, search: TaskSourceFileSearch
) -> tuple[int, Sequence[tuple[File, Experiment]]]:
    base_stmt = (
        select(File, Experiment)
        .select_from(File)
        .join(Experiment, Experiment.id == File.experiment_id)
        .options(
            load_only(File.id, File.name, File.extension, File.experiment_id),
            load_only(Experiment.name),
        )
    )
    if search.name:
        base_stmt = base_stmt.where(File.name.icontains(search.name))
    if search.extension:
        base_stmt = base_stmt.where(File.extension == search.extension)
    if search.experiment_name:
        base_stmt = base_stmt.where(Experiment.name.icontains(search.experiment_name))
    if not search.include_deleted:
        base_stmt = base_stmt.where(Experiment.is_deleted == False, File.is_deleted == False)
    return query_paged_data(db, base_stmt, search.offset, search.limit, scalars=False)
