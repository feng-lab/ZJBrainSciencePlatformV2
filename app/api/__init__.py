import functools
import json
from datetime import date, datetime
from json import JSONEncoder
from typing import Any, Callable

from sqlalchemy.orm import Session
from sqlalchemy.sql.roles import WhereHavingRole
from starlette.responses import JSONResponse

from app.common.exception import ServiceError
from app.common.localization import Entity, translate_message
from app.db import OrmModel, common_crud
from app.db.crud import human_subject as crud_human_subject
from app.db.orm import (
    Atlas,
    AtlasBehavioralDomain,
    AtlasParadigmClass,
    AtlasRegion,
    AtlasRegionLink,
    Device,
    Experiment,
    Task,
    User,
    VirtualFile,
)
from app.model.response import Response


class ApiJsonEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        match o:
            case datetime():
                return o.strftime("%Y-%m-%d %H:%M:%S")
            case date():
                return o.strftime("%Y-%m-%d")
            case _:
                return super().default(o)


class ApiJsonResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return json.dumps(
            content, ensure_ascii=False, allow_nan=False, indent=None, separators=(",", ":"), cls=ApiJsonEncoder
        ).encode("UTF-8")


def wrap_api_response(func: Callable[..., Any]):
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> ApiJsonResponse:
        response_data = func(*args, **kwargs)
        success_message = translate_message("success")
        response = Response(data=response_data, message=success_message)
        json_response = ApiJsonResponse(response.dict())
        return json_response

    return wrapper


def check_experiment_exists(db: Session, experiment_id: int) -> None:
    return _check_exists(db, Experiment, Entity.experiment, id_=experiment_id)


def check_user_exists(db: Session, user_id: int) -> None:
    return _check_exists(db, User, Entity.user, id_=user_id)


def check_device_exists(db: Session, device_id: int) -> None:
    return _check_exists(db, Device, Entity.device, id_=device_id)


def check_human_subject_exists(db: Session, user_id: int) -> None:
    if not crud_human_subject.check_human_subject_exists(db, user_id):
        raise ServiceError.not_found(Entity.human_subject)


def check_virtual_file_exists(db: Session, file_id: int) -> None:
    _check_exists(db, VirtualFile, Entity.file, id_=file_id)


def check_task_exists(db: Session, task_id: int) -> None:
    _check_exists(db, Task, Entity.task, id_=task_id)


def check_atlas_exists(db: Session, atlas_id: int) -> None:
    _check_exists(db, Atlas, Entity.atlas, id_=atlas_id)


def check_atlas_region_exists(db: Session, atlas_region_id: int) -> None:
    _check_exists(db, AtlasRegion, Entity.atlas_region, id_=atlas_region_id)


def check_atlas_region_link_exists(db: Session, atlas_region_link_id: int) -> None:
    _check_exists(db, AtlasRegionLink, Entity.atlas_region_link, id_=atlas_region_link_id)


def check_atlas_behavioral_domain_exists(db: Session, atlas_behavioral_domain_id: int) -> None:
    _check_exists(db, AtlasBehavioralDomain, Entity.atlas_behavioral_domain, id_=atlas_behavioral_domain_id)


def check_atlas_paradigm_class_exists(db: Session, atlas_paradigm_class_id: int) -> None:
    _check_exists(db, AtlasParadigmClass, Entity.atlas_paradigm_class, id_=atlas_paradigm_class_id)


def _check_exists(
    db: Session,
    table: type[OrmModel],
    entity: Entity,
    *,
    id_: int | None = None,
    where: list[WhereHavingRole] | None = None,
) -> None:
    exists = common_crud.exists_row(db, table, id_=id_, where=where)
    if not exists:
        raise ServiceError.not_found(entity)
