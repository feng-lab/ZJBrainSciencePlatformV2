from typing import Sequence

from sqlalchemy import and_, select
from sqlalchemy.orm import Session, immediateload, joinedload, load_only

from app.db.crud.user import load_user_info
from app.db.orm import Experiment, Paradigm, StorageFile, VirtualFile
from app.model.schema import PageParm


def load_paradigm_creator_option():
    return load_user_info(joinedload(Paradigm.creator_obj))


def load_paradigm_files_option():
    return immediateload(Paradigm.exist_virtual_files).load_only(VirtualFile.id)


def get_paradigm_by_id(db: Session, paradigm_id: int) -> Paradigm | None:
    stmt = (
        select(Paradigm)
        .where(Paradigm.id == paradigm_id, Paradigm.is_deleted == False)
        .options(load_paradigm_creator_option(), load_paradigm_files_option())
    )
    paradigm = db.execute(stmt).scalar()
    return paradigm


def list_paradigm_files(db: Session, paradigm_id: int) -> list[int]:
    stmt = select(VirtualFile.id).join(Paradigm.exist_virtual_files).where(VirtualFile.paradigm_id == paradigm_id)
    result = db.execute(stmt).scalars().all()
    return list(result)


def search_paradigms(db: Session, experiment_id: int, page_param: PageParm) -> list[Paradigm]:
    stmt = (
        select(Paradigm)
        .where(Paradigm.experiment_id == experiment_id)
        .join(Experiment, and_(Paradigm.experiment_id == Experiment.id, Experiment.is_deleted == False))
        .offset(page_param.offset)
        .limit(page_param.limit)
        .options(load_paradigm_creator_option(), load_paradigm_files_option())
    )
    if not page_param.include_deleted:
        stmt = stmt.where(Paradigm.is_deleted == False)
    paradigms = db.execute(stmt).scalars().all()
    return list(paradigms)


def get_paradigm_file_infos(db: Session, paradigm_id: int) -> Sequence[VirtualFile]:
    stmt = (
        select(VirtualFile)
        .select_from(Experiment)
        .join(Experiment.exists_paradigms)
        .join(Paradigm.exist_virtual_files)
        .where(Paradigm.id == paradigm_id)
        .options(
            immediateload(VirtualFile.exist_storage_files).load_only(StorageFile.id, StorageFile.storage_path),
            load_only(VirtualFile.id),
        )
    )
    virtual_files = db.execute(stmt).scalars().all()
    return virtual_files
