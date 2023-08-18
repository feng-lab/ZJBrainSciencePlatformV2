from fastapi import APIRouter, Depends, Query

from app.api import (
    check_atlas_behavioral_domain_exists,
    check_atlas_exists,
    check_atlas_paradigm_class_exists,
    check_atlas_region_exists,
    wrap_api_response,
)
from app.common.context import AllUserContext
from app.common.localization import Entity
from app.db import common_crud
from app.db.crud import atlas as crud
from app.db.orm import (
    Atlas,
    AtlasBehavioralDomain,
    AtlasParadigmClass,
    AtlasRegion,
    AtlasRegionBehavioralDomain,
    AtlasRegionLink,
    AtlasRegionParadigmClass,
)
from app.model import convert
from app.model.field import ID
from app.model.request import DeleteModelRequest
from app.model.response import NoneResponse, Page, Response
from app.model.schema import (
    AtlasBehavioralDomainCreate,
    AtlasBehavioralDomainTreeInfo,
    AtlasBehavioralDomainUpdate,
    AtlasCreate,
    AtlasInfo,
    AtlasParadigmClassCreate,
    AtlasParadigmClassTreeInfo,
    AtlasParadigmClassUpdate,
    AtlasRegionBehavioralDomainCreate,
    AtlasRegionBehavioralDomainDict,
    AtlasRegionBehavioralDomainUpdate,
    AtlasRegionCreate,
    AtlasRegionInfo,
    AtlasRegionLinkCreate,
    AtlasRegionLinkInfo,
    AtlasRegionLinkUpdate,
    AtlasRegionParadigmClassCreate,
    AtlasRegionParadigmClassDict,
    AtlasRegionParadigmClassUpdate,
    AtlasRegionTreeInfo,
    AtlasRegionUpdate,
    AtlasSearch,
    AtlasUpdate,
)

router = APIRouter(tags=["atlas"])


@router.post("/api/createAtlas", description="创建脑图谱", response_model=Response[int])
@wrap_api_response
def create_atlas(create: AtlasCreate, ctx: AllUserContext = Depends()) -> int:
    return common_crud.insert_row(ctx.db, Atlas, create.dict(), commit=True, raise_on_fail=True)


@router.delete("/api/deleteAtlas", description="删除脑图谱", response_model=NoneResponse)
@wrap_api_response
def delete_atlas(request: DeleteModelRequest, ctx: AllUserContext = Depends()) -> None:
    common_crud.update_row_as_deleted(
        ctx.db, Atlas, id_=request.id, commit=True, raise_on_fail=True
    )


@router.post("/api/updateAtlas", description="更新脑图谱", response_model=NoneResponse)
@wrap_api_response
def update_atlas(request: AtlasUpdate, ctx: AllUserContext = Depends()) -> None:
    check_atlas_exists(ctx.db, request.id)
    common_crud.update_row(
        ctx.db, Atlas, request.dict(exclude={"id"}), id_=request.id, commit=True, raise_on_fail=True
    )


@router.get("/api/getAtlasInfo", description="获取脑图谱详情", response_model=Response[AtlasInfo])
@wrap_api_response
def get_atlas_info(
    atlas_id: ID = Query(description="脑图谱ID"), ctx: AllUserContext = Depends()
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
    search: AtlasSearch = Depends(), ctx: AllUserContext = Depends()
) -> Page[AtlasInfo]:
    total, atlas_orm = crud.search_atlases(ctx.db, search)
    atlas_infos = convert.map_list(convert.atlas_orm_2_info, atlas_orm)
    return Page(total=total, items=atlas_infos)


@router.post("/api/createAtlasRegion", description="创建脑图谱区域", response_model=Response[int])
@wrap_api_response
def create_atlas_region(create: AtlasRegionCreate, ctx: AllUserContext = Depends()) -> int:
    check_atlas_exists(ctx.db, create.atlas_id)
    return common_crud.insert_row(
        ctx.db, AtlasRegion, create.dict(), commit=True, raise_on_fail=True
    )


@router.delete("/api/deleteAtlasRegion", description="删除脑图谱区域", response_model=NoneResponse)
@wrap_api_response
def delete_atlas_region(request: DeleteModelRequest, ctx: AllUserContext = Depends()) -> None:
    common_crud.update_row_as_deleted(
        ctx.db, AtlasRegion, id_=request.id, commit=True, raise_on_fail=True
    )


@router.post("/api/updateAtlasRegion", description="更新脑图谱区域", response_model=NoneResponse)
@wrap_api_response
def update_atlas_region(request: AtlasRegionUpdate, ctx: AllUserContext = Depends()) -> None:
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
    ctx: AllUserContext = Depends(),
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
    atlas_id: ID = Query(description="脑图谱ID"), ctx: AllUserContext = Depends()
) -> list[AtlasRegionTreeInfo]:
    regions = crud.list_atlas_regions_by_atlas_id(ctx.db, atlas_id)
    region_tree_nodes = convert.map_list(convert.atlas_region_orm_2_tree_node, regions)
    region_trees = build_trees(region_tree_nodes)
    region_tree_infos = convert.map_list(convert.atlas_region_tree_node_2_info, region_trees)
    return region_tree_infos


def build_trees(tree_nodes: list) -> list:
    node_map = {node.id: node for node in tree_nodes}
    roots = []
    for node in tree_nodes:
        if node.parent_id is None or node.parent_id not in node_map:
            roots.append(node)
        else:
            parent = node_map[node.parent_id]
            parent.children.append(node)
    return roots


@router.post("/api/createAtlasRegionLink", description="创建脑区连接", response_model=Response[int])
@wrap_api_response
def create_atlas_region_link(
    create: AtlasRegionLinkCreate, ctx: AllUserContext = Depends()
) -> int:
    check_atlas_exists(ctx.db, create.atlas_id)
    return common_crud.insert_row(
        ctx.db, AtlasRegionLink, create.dict(), commit=True, raise_on_fail=True
    )


@router.delete("/api/deleteAtlasRegionLink", description="删除脑区连接", response_model=NoneResponse)
@wrap_api_response
def delete_atlas_region_link(
    request: DeleteModelRequest, ctx: AllUserContext = Depends()
) -> None:
    common_crud.update_row_as_deleted(
        ctx.db, AtlasRegionLink, id_=request.id, commit=True, raise_on_fail=True
    )


@router.post("/api/updateAtlasRegionLink", description="更新脑区连接", response_model=NoneResponse)
@wrap_api_response
def update_atlas_region_link(
    update: AtlasRegionLinkUpdate, ctx: AllUserContext = Depends()
) -> None:
    check_atlas_exists(ctx.db, update.atlas_id)
    check_atlas_region_exists(ctx.db, update.id)
    common_crud.update_row(
        ctx.db,
        AtlasRegionLink,
        update.dict(exclude={"id"}),
        id_=update.id,
        commit=True,
        raise_on_fail=True,
    )


@router.get(
    "/api/getAtlasRegionLinkInfo",
    description="获取脑区连接详情",
    response_model=Response[AtlasRegionLinkInfo],
)
@wrap_api_response
def get_atlas_region_link_info(
    id_: ID | None = Query(None, alias="id", description="脑区连接系统ID"),
    atlas_id: ID | None = Query(None, description="脑图谱ID"),
    link_id: ID | None = Query(None, description="脑区连接ID"),
    ctx: AllUserContext = Depends(),
) -> AtlasRegionLinkInfo:
    link_orm = crud.get_atlas_region_link(ctx.db, id_, link_id, atlas_id)
    link_info = convert.atlas_region_link_orm_2_info(link_orm)
    return link_info


@router.post("/api/createBehavioralDomain", description="创建脑图谱行为域", response_model=Response[int])
@wrap_api_response
def create_behavioral_domain(
    create: AtlasBehavioralDomainCreate, ctx: AllUserContext = Depends()
) -> int:
    check_atlas_exists(ctx.db, create.atlas_id)
    domain_id = common_crud.insert_row(
        ctx.db, AtlasBehavioralDomain, create.dict(), commit=True, raise_on_fail=True
    )
    return domain_id


@router.delete("/api/deleteBehavioralDomain", description="删除脑图谱行为域", response_model=NoneResponse)
@wrap_api_response
def delete_behavioral_domain(
    request: DeleteModelRequest, ctx: AllUserContext = Depends()
) -> None:
    common_crud.update_row_as_deleted(
        ctx.db, AtlasBehavioralDomain, id_=request.id, commit=True, raise_on_fail=True
    )


@router.post(
    "/api/updateAtlasBehavioralDomain", description="更新脑图谱行为域", response_model=NoneResponse
)
@wrap_api_response
def update_atlas_region_link(
    update: AtlasBehavioralDomainUpdate, ctx: AllUserContext = Depends()
) -> None:
    check_atlas_exists(ctx.db, update.atlas_id)
    check_atlas_behavioral_domain_exists(ctx.db, update.id)
    common_crud.update_row(
        ctx.db,
        AtlasBehavioralDomain,
        update.dict(exclude={"id"}),
        id_=update.id,
        commit=True,
        raise_on_fail=True,
    )


@router.get(
    "/api/getAtlasBehavioralDomainTrees",
    description="获取脑图谱行为域树",
    response_model=Response[list[AtlasBehavioralDomainTreeInfo]],
)
@wrap_api_response
def get_atlas_behavioral_domain_trees(
    atlas_id: ID = Query(description="脑图谱ID"), ctx: AllUserContext = Depends()
) -> list[AtlasBehavioralDomainTreeInfo]:
    domains = crud.list_atlas_behavioral_domains_by_atlas_id(ctx.db, atlas_id)
    domain_tree_nodes = convert.map_list(convert.atlas_behavioral_domain_orm_2_tree_node, domains)
    domain_trees = build_trees(domain_tree_nodes)
    domain_tree_infos = convert.map_list(
        convert.atlas_behavioral_domain_tree_node_2_info, domain_trees
    )
    return domain_tree_infos


@router.post(
    "/api/createAtlasRegionBehavioralDomain", description="创建脑区相关的行为域", response_model=Response[int]
)
@wrap_api_response
def create_atlas_region_behavioral_domain(
    create: AtlasRegionBehavioralDomainCreate, ctx: AllUserContext = Depends()
) -> int:
    check_atlas_exists(ctx.db, create.atlas_id)
    check_atlas_region_exists(ctx.db, create.region_id)
    return common_crud.insert_row(
        ctx.db, AtlasRegionBehavioralDomain, create.dict(), commit=True, raise_on_fail=True
    )


@router.delete(
    "/api/deleteAtlasRegionBehavioralDomain", description="删除脑区相关的行为域", response_model=NoneResponse
)
@wrap_api_response
def delete_atlas_region_behavioral_domain(
    request: DeleteModelRequest, ctx: AllUserContext = Depends()
) -> None:
    common_crud.update_row_as_deleted(
        ctx.db, AtlasRegionBehavioralDomain, id_=request.id, commit=True, raise_on_fail=True
    )


@router.post(
    "/api/updateAtlasRegionBehavioralDomain", description="更新脑区相关的行为域", response_model=NoneResponse
)
@wrap_api_response
def update_atlas_region_behavioral_domain(
    update: AtlasRegionBehavioralDomainUpdate, ctx: AllUserContext = Depends()
) -> None:
    check_atlas_exists(ctx.db, update.atlas_id)
    check_atlas_region_exists(ctx.db, update.id)
    common_crud.update_row(
        ctx.db,
        AtlasRegionBehavioralDomain,
        update.dict(exclude={"id"}),
        id_=update.id,
        commit=True,
        raise_on_fail=True,
    )


@router.get(
    "/api/getAtlasRegionBehavioralDomains",
    description="获取脑区相关的行为域详情",
    response_model=Response[AtlasRegionBehavioralDomainDict],
)
@wrap_api_response
def get_atlas_region_behavioral_domains(
    atlas_id: ID = Query(description="脑图谱ID"),
    region_id: ID = Query(description="脑区ID"),
    ctx: AllUserContext = Depends(),
) -> AtlasRegionBehavioralDomainDict:
    region_domains_orm = crud.list_atlas_region_behavioral_domains(ctx.db, atlas_id, region_id)
    region_domains_dict = convert.atlas_region_associated_model_2_dict(region_domains_orm)
    return region_domains_dict


@router.post("/api/createParadigmClass", description="创建脑图谱范例集", response_model=Response[int])
@wrap_api_response
def create_paradigm_class(
    create: AtlasParadigmClassCreate, ctx: AllUserContext = Depends()
) -> int:
    check_atlas_exists(ctx.db, create.atlas_id)
    paradigm_class_id = common_crud.insert_row(
        ctx.db, AtlasParadigmClass, create.dict(), commit=True, raise_on_fail=True
    )
    return paradigm_class_id


@router.delete("/api/deleteParadigmClass", description="删除脑图谱范例集", response_model=NoneResponse)
@wrap_api_response
def delete_paradigm_class(request: DeleteModelRequest, ctx: AllUserContext = Depends()) -> None:
    common_crud.update_row_as_deleted(
        ctx.db, AtlasParadigmClass, id_=request.id, commit=True, raise_on_fail=True
    )


@router.post("/api/updateParadigmClass", description="更新脑图谱范例集", response_model=NoneResponse)
@wrap_api_response
def update_paradigm_class(
    update: AtlasParadigmClassUpdate, ctx: AllUserContext = Depends()
) -> None:
    check_atlas_exists(ctx.db, update.atlas_id)
    check_atlas_paradigm_class_exists(ctx.db, update.id)
    common_crud.update_row(
        ctx.db,
        AtlasParadigmClass,
        update.dict(exclude={"id"}),
        id_=update.id,
        commit=True,
        raise_on_fail=True,
    )


@router.get(
    "/api/getParadigmClassTrees",
    description="获取脑图谱范例集树",
    response_model=Response[list[AtlasParadigmClassTreeInfo]],
)
@wrap_api_response
def get_paradigm_class_trees(
    atlas_id: ID = Query(description="脑图谱ID"), ctx: AllUserContext = Depends()
) -> list[AtlasParadigmClassTreeInfo]:
    paradigm_classes = crud.list_atlas_paradigm_class_by_atlas_id(ctx.db, atlas_id)
    paradigm_class_tree_nodes = convert.map_list(
        convert.atlas_paradigm_class_orm_2_tree_node, paradigm_classes
    )
    paradigm_class_trees = build_trees(paradigm_class_tree_nodes)
    paradigm_class_tree_infos = convert.map_list(
        convert.atlas_paradigm_class_tree_node_2_info, paradigm_class_trees
    )
    return paradigm_class_tree_infos


@router.post(
    "/api/createAtlasRegionParadigmClass", description="创建脑区相关的范例集", response_model=Response[int]
)
@wrap_api_response
def create_atlas_region_paradigm_class(
    create: AtlasRegionParadigmClassCreate, ctx: AllUserContext = Depends()
) -> int:
    check_atlas_exists(ctx.db, create.atlas_id)
    check_atlas_region_exists(ctx.db, create.region_id)
    return common_crud.insert_row(
        ctx.db, AtlasRegionParadigmClass, create.dict(), commit=True, raise_on_fail=True
    )


@router.delete(
    "/api/deleteAtlasRegionParadigmClass", description="删除脑区相关的范例集", response_model=NoneResponse
)
@wrap_api_response
def delete_atlas_region_paradigm_class(
    request: DeleteModelRequest, ctx: AllUserContext = Depends()
) -> None:
    common_crud.update_row_as_deleted(
        ctx.db, AtlasRegionParadigmClass, id_=request.id, commit=True, raise_on_fail=True
    )


@router.post(
    "/api/updateAtlasRegionParadigmClass", description="更新脑区相关的范例集", response_model=NoneResponse
)
@wrap_api_response
def update_atlas_region_paradigm_class(
    update: AtlasRegionParadigmClassUpdate, ctx: AllUserContext = Depends()
) -> None:
    check_atlas_exists(ctx.db, update.atlas_id)
    check_atlas_region_exists(ctx.db, update.id)
    common_crud.update_row(
        ctx.db,
        AtlasRegionParadigmClass,
        update.dict(exclude={"id"}),
        id_=update.id,
        commit=True,
        raise_on_fail=True,
    )


@router.get(
    "/api/getAtlasRegionParadigmClasses",
    description="获取脑区相关的范例集详情",
    response_model=Response[AtlasRegionBehavioralDomainDict],
)
@wrap_api_response
def get_atlas_region_paradigm_classes(
    atlas_id: ID = Query(description="脑图谱ID"),
    region_id: ID = Query(description="脑区ID"),
    ctx: AllUserContext = Depends(),
) -> AtlasRegionParadigmClassDict:
    region_domains_orm = crud.list_atlas_region_paradigm_classes(ctx.db, atlas_id, region_id)
    region_domains_dict = convert.atlas_region_associated_model_2_dict(region_domains_orm)
    return region_domains_dict
