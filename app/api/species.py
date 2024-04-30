from fastapi import APIRouter, Depends

from app.api import wrap_api_response
from app.common.context import HumanSubjectContext, ResearcherContext
from app.common.exception import ServiceError
from app.common.localization import Entity
from app.db import common_crud
from app.db.orm import Species
from app.model import convert
from app.model.request import DeleteModelRequest
from app.model.response import NoneResponse, Response
from app.model.schema import CreateSpeciesRequest, SpeciesInfo, UpdateSpeciesRequest

router = APIRouter(tags=["species"])


@router.post("/api/createSpecies", description="创建物种", response_model=Response[int])
@wrap_api_response
def create_species(request: CreateSpeciesRequest, ctx: ResearcherContext = Depends()) -> int:
    species_dict = request.dict()
    species_id = common_crud.insert_row(ctx.db, Species, species_dict, commit=False)
    if species_id is None:
        raise ServiceError.database_fail()

    ctx.db.commit()
    return species_id


@router.post("/api/getSpeciesInfo", description="获取物种名称详情", response_model=Response[SpeciesInfo])
@wrap_api_response
def get_species_info(species_id: int, ctx: HumanSubjectContext = Depends()) -> SpeciesInfo:
    orm_species = common_crud.get_row_by_id(ctx.db, Species, species_id)
    if orm_species is None:
        raise ServiceError.not_found(Entity.species)
    species_info = convert.species_orm_2_info(orm_species)
    return species_info

@router.post("/api/getAllSpeciesInfo", description="获取物种名称详情", response_model=Response[SpeciesInfo])




@router.post("/api/updateSpecies", description="更新物种名称", response_model=NoneResponse)
@wrap_api_response
def update_species(request: UpdateSpeciesRequest, ctx: ResearcherContext = Depends()) -> None:
    orm_species = common_crud.get_row_by_id(ctx.db, Species, request.id)
    if orm_species is None:
        raise ServiceError.not_found(Entity.species)
    species_dict = request.dict(exclude_unset=True)
    success = common_crud.update_row(ctx.db, Species, species_dict, id_=request.id, commit=True)
    if not success:
        raise ServiceError.database_fail()


@router.delete("/api/deleteSpecies", description="删除数据集", response_model=NoneResponse)
@wrap_api_response
def delete_species(request: DeleteModelRequest, ctx: ResearcherContext = Depends()) -> None:
    success = common_crud.bulk_update_rows_as_deleted(ctx.db, Species, ids=[request.id], commit=True)
    if not success:
        raise ServiceError.database_fail()
