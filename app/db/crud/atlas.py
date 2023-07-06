from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.common.exception import ServiceError
from app.common.localization import Entity
from app.db.crud import query_pages
from app.db.orm import Atlas, AtlasRegion
from app.model.field import ID
from app.model.schema import AtlasSearch


def search_atlases(db: Session, search: AtlasSearch) -> tuple[int, Sequence[Atlas]]:
    base_stmt = select(Atlas).select_from(Atlas)
    if search.name:
        base_stmt = base_stmt.where(Atlas.name.icontains(search.name))
    if not search.include_deleted:
        base_stmt = base_stmt.where(Atlas.is_deleted == False)
    return query_pages(db, base_stmt, search.offset, search.limit)


# noinspection PyTypeChecker
def get_atlas_region(
    db: Session, id_: ID | None, region_id: ID | None, atlas_id: ID | None
) -> AtlasRegion:
    stmt = (
        select(AtlasRegion)
        .join(Atlas, Atlas.id == AtlasRegion.atlas_id)
        .where(Atlas.is_deleted == False, AtlasRegion.is_deleted == False)
    )
    if id_ is not None:
        stmt = stmt.where(AtlasRegion.id == id_)
    elif atlas_id is not None:
        stmt = stmt.where(AtlasRegion.atlas_id == atlas_id, AtlasRegion.region_id == region_id)
    else:
        raise ServiceError.params_error("both atlas_id and id are null")

    atlas_region = db.execute(stmt).scalar()
    if atlas_region is None:
        raise ServiceError.not_found(Entity.atlas_region)
    return atlas_region


# noinspection PyTypeChecker
def list_atlas_regions_by_atlas_id(db: Session, atlas_id: ID) -> Sequence[AtlasRegion]:
    stmt = (
        select(
            AtlasRegion.id,
            AtlasRegion.atlas_id,
            AtlasRegion.region_id,
            AtlasRegion.parent_id,
            AtlasRegion.description,
            AtlasRegion.acronym,
        )
        .join(Atlas, Atlas.id == AtlasRegion.atlas_id)
        .where(
            AtlasRegion.atlas_id == atlas_id,
            Atlas.is_deleted == False,
            AtlasRegion.is_deleted == False,
        )
    )
    atlas_regions = db.execute(stmt).all()
    return atlas_regions
