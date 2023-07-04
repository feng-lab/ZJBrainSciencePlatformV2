from fastapi import APIRouter, Depends

from app.api import wrap_api_response
from app.common.context import ResearcherContext
from app.common.exception import ServiceError
from app.db import common_crud
from app.db.orm import Atlas
from app.model.response import Response
from app.model.schema import AtlasCreate

router = APIRouter(tags=["atlas"])


@router.post("/api/createAtlas", description="创建脑图谱", response_model=Response[int])
@wrap_api_response
def create_atlas(create: AtlasCreate, ctx: ResearcherContext = Depends()) -> int:
    atlas_id = common_crud.insert_row(ctx.db, Atlas, create.dict(), commit=True)
    if atlas_id is None:
        raise ServiceError.database_fail()
    return atlas_id
