import logging
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, immediateload

from app.db.crud import query_paged_data
from app.db.orm import StorageFile, VirtualFile
from app.model.schema import FileSearch

logger = logging.getLogger(__name__)


def get_file_extensions(db: Session, experiment_id: int) -> Sequence[str]:
    stmt = (
        select(VirtualFile.file_type)
        .where(
            VirtualFile.experiment_id == experiment_id,
            VirtualFile.is_deleted == False,
            VirtualFile.paradigm_id.is_(None),
        )
        .group_by(VirtualFile.file_type)
    )
    extensions = db.execute(stmt).scalars().all()
    return extensions


def search_files(db: Session, search: FileSearch) -> tuple[int, Sequence[VirtualFile]]:
    base_stmt = (
        select(VirtualFile)
        .where(VirtualFile.paradigm_id.is_(None))
        .order_by(VirtualFile.id.asc())
        .options(immediateload(VirtualFile.storage_files))
    )
    if search.experiment_id is not None:
        base_stmt = base_stmt.where(VirtualFile.experiment_id == search.experiment_id)
    if search.name:
        base_stmt = base_stmt.where(VirtualFile.name.icontains(search.name))
    if search.file_type:
        base_stmt = base_stmt.where(VirtualFile.extension.icontains(search.file_type))
    if not search.include_deleted:
        base_stmt = base_stmt.where(VirtualFile.is_deleted == False)

    return query_paged_data(db, base_stmt, search.offset, search.limit)


def get_file_download_info(db: Session, virtual_file_id: int) -> tuple[str | None, str | None]:
    stmt = (
        select(StorageFile.name, StorageFile.storage_path)
        .join(VirtualFile.storage_files)
        .where(
            VirtualFile.id == virtual_file_id,
            StorageFile.name == VirtualFile.name,
            VirtualFile.is_deleted == False,
            StorageFile.is_deleted == False,
        )
    )
    storage_file = db.execute(stmt).one_or_none()
    if storage_file is None:
        return None, None
    return storage_file.name, storage_file.storage_path


def get_db_storage_paths(db: Session, virtual_file_id: int) -> Sequence[str]:
    stmt = (
        select(StorageFile.storage_path)
        .join(VirtualFile.storage_files)
        .where(
            VirtualFile.id == virtual_file_id,
            VirtualFile.is_deleted == False,
            StorageFile.is_deleted == False,
        )
    )
    storage_file_paths = db.execute(stmt).scalars().all()
    return storage_file_paths
