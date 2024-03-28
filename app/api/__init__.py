import asyncio
import base64
import functools
import json
from datetime import date, datetime
from json import JSONEncoder
from typing import Any, Callable

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
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
    Dataset,
    EEGData,
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
    def response_2_json(response: Response) -> ApiJsonResponse:
        success_message = translate_message("success")
        response = Response(data=response, message=success_message)
        json_response = ApiJsonResponse(response.dict())
        return json_response

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs) -> ApiJsonResponse:
        return response_2_json(await func(*args, **kwargs))

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs) -> ApiJsonResponse:
        return response_2_json(func(*args, **kwargs))

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


AUTH_AES_KEY: bytes = b"#030doH2<FIb#b88"
aes_cipher = AES.new(AUTH_AES_KEY, AES.MODE_ECB)


def encrypt_password(data: str) -> str:
    pad_data = pad(data.encode("UTF-8"), AES.block_size, style="pkcs7")
    enc_data = aes_cipher.encrypt(pad_data)
    base64_enc_data = base64.b64encode(enc_data).decode("ASCII")
    return base64_enc_data


def decrypt_password(data: str) -> str:
    enc_data = base64.b64decode(data.encode("ASCII"))
    pad_data = aes_cipher.decrypt(enc_data)
    data = unpad(pad_data, AES.block_size, style="pkcs7").decode("UTF-8")
    return data


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


def check_dataset_exists(db: Session, dataset_id: int) -> None:
    _check_exists(db, Dataset, Entity.dataset, id_=dataset_id)


def check_eegdata_exists(db: Session, eegdata_id: int) -> None:
    _check_exists(db, EEGData, Entity.EEGData, id_=eegdata_id)


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
