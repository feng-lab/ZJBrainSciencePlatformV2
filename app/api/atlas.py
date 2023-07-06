from fastapi import APIRouter, Depends, Query

from app.api import check_atlas_exists, check_atlas_region_exists, wrap_api_response
from app.common.context import HumanSubjectContext, ResearcherContext
from app.common.localization import Entity
from app.db import common_crud
from app.db.crud import atlas as crud
from app.db.orm import Atlas, AtlasRegion
from app.model import convert
from app.model.field import ID
from app.model.request import DeleteModelRequest
from app.model.response import NoneResponse, Page, Response
from app.model.schema import (
    AtlasCreate,
    AtlasInfo,
    AtlasRegionCreate,
    AtlasRegionInfo,
    AtlasRegionTreeInfo,
    AtlasRegionTreeNode,
    AtlasRegionUpdate,
    AtlasSearch,
    AtlasUpdate,
)

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


@router.post("/api/updateAtlas", description="更新脑图谱", response_model=NoneResponse)
@wrap_api_response
def update_atlas(request: AtlasUpdate, ctx: ResearcherContext = Depends()) -> None:
    check_atlas_exists(ctx.db, request.id)
    common_crud.update_row(
        ctx.db, Atlas, request.dict(exclude={"id"}), id_=request.id, commit=True, raise_on_fail=True
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


@router.get(
    "/api/getAtlasesByPage", description="分页获取脑图谱详情", response_model=Response[Page[AtlasInfo]]
)
@wrap_api_response
def get_atlases_by_page(
    search: AtlasSearch = Depends(), ctx: HumanSubjectContext = Depends()
) -> Page[AtlasInfo]:
    total, atlas_orm = crud.search_atlases(ctx.db, search)
    atlas_infos = convert.map_list(convert.atlas_orm_2_info, atlas_orm)
    return Page(total=total, items=atlas_infos)


@router.post("/api/createAtlasRegion", description="创建脑图谱区域", response_model=Response[int])
@wrap_api_response
def create_atlas_region(create: AtlasRegionCreate, ctx: ResearcherContext = Depends()) -> int:
    return common_crud.insert_row(
        ctx.db, AtlasRegion, create.dict(), commit=True, raise_on_fail=True
    )


@router.delete("/api/deleteAtlasRegion", description="删除脑图谱区域", response_model=NoneResponse)
@wrap_api_response
def delete_atlas_region(request: DeleteModelRequest, ctx: ResearcherContext = Depends()) -> None:
    common_crud.update_row_as_deleted(
        ctx.db, AtlasRegion, id_=request.id, commit=True, raise_on_fail=True
    )


@router.post("/api/updateAtlasRegion", description="更新脑图谱区域", response_model=NoneResponse)
@wrap_api_response
def update_atlas_region(request: AtlasRegionUpdate, ctx: ResearcherContext = Depends()) -> None:
    check_atlas_region_exists(ctx.db, request.id)
    common_crud.update_row(
        ctx.db,
        AtlasRegion,
        request.dict(exclude={"id"}),
        id_=request.id,
        commit=True,
        raise_on_fail=True,
    )


@router.get(
    "/api/getAtlasRegionInfo",
    description="获取脑图谱区域详情，可以根据id或region_id+atlas_id查询",
    response_model=Response[AtlasRegionInfo],
)
@wrap_api_response
def get_atlas_region_info(
    id_: ID | None = Query(None, alias="id", description="脑图谱区域系统ID"),
    region_id: ID | None = Query(None, description="脑图谱区域ID"),
    atlas_id: ID | None = Query(None, description="脑图谱ID"),
    ctx: HumanSubjectContext = Depends(),
) -> AtlasRegionInfo:
    atlas_region_orm = crud.get_atlas_region(ctx.db, id_, region_id, atlas_id)
    atlas_region_info = convert.atlas_region_orm_2_info(atlas_region_orm)
    return atlas_region_info


@router.get(
    "/api/getAtlasRegionTrees",
    description="获取脑图谱区域树形结构",
    response_model=Response[list[AtlasRegionTreeInfo]],
)
@wrap_api_response
def get_atlas_region_trees(
    atlas_id: ID = Query(description="脑图谱ID"), ctx: HumanSubjectContext = Depends()
) -> list[AtlasRegionTreeInfo]:
    regions = crud.list_atlas_regions_by_atlas_id(ctx.db, atlas_id)
    region_tree_nodes = convert.map_list(convert.atlas_region_orm_2_tree_node, regions)
    region_trees = build_atlas_region_trees(region_tree_nodes)
    region_tree_infos = convert.map_list(convert.atlas_region_tree_node_2_info, region_trees)
    return region_tree_infos


def build_atlas_region_trees(atlas_regions: list[AtlasRegionTreeNode]) -> list[AtlasRegionTreeNode]:
    regions_map = {region.id: region for region in atlas_regions}
    roots = []
    for region in atlas_regions:
        if region.parent_id is None:
            roots.append(region)
        else:
            parent = regions_map[region.parent_id]
            parent.children.append(region)
    return roots
