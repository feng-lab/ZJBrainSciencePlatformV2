import functools
import json
from contextvars import ContextVar
from datetime import date, datetime
from json import JSONEncoder
from typing import Any, Callable

from sqlalchemy.orm import Session
from sqlalchemy.sql.roles import WhereHavingRole
from starlette.responses import JSONResponse

from app.common.exception import ServiceError
from app.common.message_location import MessageLocale, translate_message
from app.db import OrmModel, common_crud
from app.db.crud import human_subject as crud_human_subject
from app.db.orm import Device, Experiment, Task, User, VirtualFile
from app.model.response import Response

locale_ctxvar = ContextVar("locale", default=MessageLocale.zh_CN)


def api_translate_message(message_id: str, *format_args: Any) -> str:
    locale = locale_ctxvar.get()
    return translate_message(message_id, locale, *format_args)


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
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=ApiJsonEncoder,
        ).encode("UTF-8")


def wrap_api_response(func: Callable[..., Any]):
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> ApiJsonResponse:
        response_data = func(*args, **kwargs)
        success_message = api_translate_message("success")
        response = Response(data=response_data, message=success_message)
        json_response = ApiJsonResponse(response.dict())
        return json_response

    return wrapper


def check_experiment_exists(db: Session, experiment_id: int) -> None:
    return _check_exists(db, Experiment, "实验不存在", id_=experiment_id)


def check_user_exists(db: Session, user_id: int) -> None:
    return _check_exists(db, User, "用户不存在", id_=user_id)


def check_device_exists(db: Session, device_id: int) -> None:
    return _check_exists(db, Device, "设备不存在", id_=device_id)


def check_human_subject_exists(db: Session, user_id: int) -> None:
    if not crud_human_subject.check_human_subject_exists(db, user_id):
        raise ServiceError.not_found("被试者不存在")


def check_virtual_file_exists(db: Session, file_id: int) -> None:
    _check_exists(db, VirtualFile, "文件不存在", id_=file_id)


def check_task_exists(db: Session, task_id: int) -> None:
    _check_exists(db, Task, "任务不存在", id_=task_id)


def _check_exists(
    db: Session,
    table: type[OrmModel],
    not_found_msg: str,
    *,
    id_: int | None = None,
    where: list[WhereHavingRole] | None = None,
) -> None:
    exists = common_crud.exists_row(db, table, id_=id_, where=where)
    if not exists:
        raise ServiceError.not_found(not_found_msg)
