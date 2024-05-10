from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.crud import query_pages
from app.db.orm import Dataset
from app.model.schema import DatasetSearch, DatasetBase
from app.db import common_crud


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
    if search.species is not None:
        base_stmt = base_stmt.where(Dataset.species.icontains(search.species))
    if search.organ is not None:
        base_stmt = base_stmt.where(Dataset.organ.icontains(search.organ))
    if search.development_stage is not None:
        base_stmt = base_stmt.where(Dataset.development_stage.icontains(search.development_stage))
    if not search.include_deleted:
        base_stmt = base_stmt.where(Dataset.is_deleted == False)
    if search.id is not None:
        base_stmt = base_stmt.where(Dataset.id == search.id)
    if search.description is not None:
        base_stmt = base_stmt.where(Dataset.description.icontains(search.description))
    if search.data_type is not None:
        base_stmt = base_stmt.where(Dataset.data_type.icontains(search.data_type))
    if search.source is not None:
        base_stmt = base_stmt.where(Dataset.source.icontains(search.source))

    return query_pages(db, base_stmt, search.offset, search.limit)


def search_data_type(db: Session, table, search: DatasetBase) -> list:
    where = []
    if search.data_type is not None:
        where.append(Dataset.data_type == search.data_type)
    if search.species is not None:
        where.append(Dataset.species == search.species)
    if search.source is not None:
        where.append(Dataset.source == search.source)
    return common_crud.get_all_ids(db, table, where)


def get_species_ids_mapping(db: Session, type:str) -> dict:
    if type =='species':
        query_type = Dataset.species
    if type == 'data_type':
        query_type = Dataset.data_type
    if type == 'source':
        query_type = Dataset.source

    col_ids = db.query(query_type, Dataset.id).distinct(query_type).all()
    col_ids_id_mapping = {}

    for species, id_ in col_ids:
        if species not in col_ids_id_mapping:
            col_ids_id_mapping[species] = []
        col_ids_id_mapping[species].append(id_)

    return col_ids_id_mapping

