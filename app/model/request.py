from enum import Enum

from fastapi import Query
from pydantic import BaseModel, Field


class GetModelsByPageParam(BaseModel):
    offset: int
    limit: int
    include_deleted: bool


def get_models_by_page(
    offset: int = Query(description="分页起始位置", default=0, ge=0),
    limit: int = Query(description="分页大小", default=10, ge=0),
    include_deleted: bool = Query(description="是否包括已删除项", default=False),
) -> GetModelsByPageParam:
    return GetModelsByPageParam(offset=offset, limit=limit, include_deleted=include_deleted)


class DeleteModelRequest(BaseModel):
    id: int


class UpdateUserAccessLevelRequest(BaseModel):
    id: int = Field(ge=0)
    access_level: int = Field(ge=0)


class UpdatePasswordRequest(BaseModel):
    old_password: str = Field(max_length=50)
    new_password: str = Field(max_length=50)


class MarkNotificationsAsReadRequest(BaseModel):
    is_all: bool = Field(description="是否标记所有通知", default=False)
    notification_ids: list[int] = Field(description="通知ID，可以有多个", default_factory=list)


class GetExperimentsByPageSortBy(Enum):
    START_TIME = "start_time"
    TYPE = "type"


class GetExperimentsByPageSortOrder(Enum):
    ASC = "asc"
    DESC = "desc"
