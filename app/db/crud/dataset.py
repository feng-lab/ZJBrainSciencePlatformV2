from typing import Sequence

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.crud import query_pages
from app.db.orm import Dataset, CumulativeDatasetSize
from app.model.schema import DatasetSearch,DatasetCollection



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


def get_species_ids_mapping(db: Session, type: str) -> dict:
    if type == "species":
        query_type = Dataset.species
    if type == "data_type":
        query_type = Dataset.data_type
    if type == "source":
        query_type = Dataset.source
    stem = select(query_type, Dataset.id).where(Dataset.is_deleted == False)
    col_ids = db.execute(stem).unique().all()
    col_ids_id_mapping = {}

    for species, id_ in col_ids:
        if species not in col_ids_id_mapping:
            col_ids_id_mapping[species] = []
        col_ids_id_mapping[species].append(id_)

    return col_ids_id_mapping


def get_species_cells_mapping(db: Session, type: str):
    if type == "species":
        query_type = Dataset.species
    if type == "data_type":
        query_type = Dataset.data_type
    if type == "source":
        query_type = Dataset.source

    stem = select(query_type, Dataset.cell_count).where(Dataset.is_deleted == False)
    col_cells = db.execute(stem).all()
    col_ids_id_mapping = {}
    for species, cells in col_cells:
        if species not in col_ids_id_mapping:
            col_ids_id_mapping[species] = []
        col_ids_id_mapping[species].append(cells)
    col_species_cells = [{'name': key, 'value': sum(cell for cell in cells if cell is not None)}for key, cells in col_ids_id_mapping.items()]
    return col_species_cells


def get_dataset_collection_info(db: Session):
    stem = select(
        Dataset.id, Dataset.description, Dataset.planed_download_per_month,Dataset.title,
        Dataset.planed_finish_date, Dataset.download_started_date
    ).where(Dataset.is_deleted == False)
    col_cells = db.execute(stem).fetchall()
    total_stmt = stem.with_only_columns(func.count())
    total = db.execute(total_stmt).scalar()
    return total, col_cells

