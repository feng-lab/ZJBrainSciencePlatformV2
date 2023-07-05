from fastapi import APIRouter, Depends, Query

from app.api import wrap_api_response
from app.common.context import HumanSubjectContext, ResearcherContext
from app.common.localization import Entity
from app.db import common_crud
from app.db.orm import Atlas
from app.model import convert
from app.model.field import ID
from app.model.request import DeleteModelRequest
from app.model.response import NoneResponse, Response
from app.model.schema import AtlasCreate, AtlasInfo

router = APIRouter(tags=["atlas"])


@router.post("/api/createAtlas", description="创建脑图谱", response_model=Response[int])
@wrap_api_response
def create_atlas(create: AtlasCreate, ctx: ResearcherContext = Depends()) -> int:
    return common_crud.insert_row(ctx.db, Atlas, create.dict(), commit=True, raise_on_fail=True)


@router.delete("/api/deleteAtlas", description="删除脑图谱", response_model=NoneResponse)
@wrap_api_response
def delete_atlas(request: DeleteModelRequest, ctx: ResearcherContext = Depends()) -> None:
    common_crud.update_row_as_deleted(
        ctx.db, Atlas, id_=request.id, commit=True, raise_on_fail=True
    )


@router.get("/api/getAtlasInfo", description="获取脑图谱详情", response_model=Response[AtlasInfo])
@wrap_api_response
def get_atlas_info(
    atlas_id: ID = Query(description="脑图谱ID"), ctx: HumanSubjectContext = Depends()
) -> AtlasInfo:
    atlas_orm = common_crud.get_row_by_id(
        ctx.db, Atlas, atlas_id, raise_on_fail=True, not_found_entity=Entity.atlas
    )
    atlas_info = convert.atlas_orm_2_info(atlas_orm)
    return atlas_info
