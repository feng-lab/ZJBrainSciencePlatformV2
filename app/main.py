import logging
from datetime import datetime
from typing import Any, Callable
from urllib.parse import parse_qsl, urlencode

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from jose import ExpiredSignatureError
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.responses import RedirectResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_500_INTERNAL_SERVER_ERROR

from app.api import ApiJsonResponse
from app.api.algorithm import router as algorithm_router
from app.api.atlas import router as atlas_router
from app.api.auth import router as auth_router
from app.api.dataset import router as dataset_router
from app.api.device import router as device_router
from app.api.experiment import router as experiment_router
from app.api.file import router as file_router
from app.api.human_subject import router as human_subject_router
from app.api.notification import router as notification_router
from app.api.paradigm import router as paradigm_router
from app.api.task import router as task_router
from app.api.user import ROOT_PASSWORD, ROOT_USERNAME
from app.api.user import router as user_router
from app.api.eegdata import router as eegdata_router
from app.common.config import config
from app.common.exception import ServiceError
from app.common.localization import MessageLocale, locale_ctxvar, translate_message
from app.common.log import ACCESS_LOGGER_NAME, log_queue_listener, request_id_ctxvar
from app.common.schedule import repeat_task
from app.common.user_auth import AccessLevel, hash_password
from app.common.util import generate_request_id
from app.db import check_database_is_up_to_date, new_db_session
from app.db.crud import send_heartbeat
from app.db.crud.experiment import insert_or_update_experiment
from app.db.crud.human_subject import get_next_human_subject_index, insert_human_subject_index
from app.db.crud.user import insert_or_update_user
from app.model.enum_filed import ExperimentType
from app.model.response import NoneResponse, ResponseCode
from app.model.schema import UserCreate

app_logger = logging.getLogger(__name__)
access_logger = logging.getLogger(ACCESS_LOGGER_NAME)

app = FastAPI(
    title="ZJBrainSciencePlatform",
    description="之江实验室 Brain Science 平台",
    openapi_tags=[
        {"name": "auth"},
        {"name": "user"},
        {"name": "notification"},
        {"name": "experiment"},
        {"name": "file"},
        {"name": "paradigm"},
        {"name": "algorithm"},
        {"name": "task"},
        {"name": "dataset"},
        {"name": "eegdata"}
    ],
    debug=config.DEBUG_MODE,
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(notification_router)
app.include_router(experiment_router)
app.include_router(file_router)
app.include_router(paradigm_router)
app.include_router(algorithm_router)
app.include_router(device_router)
app.include_router(human_subject_router)
app.include_router(task_router)
app.include_router(atlas_router)
app.include_router(dataset_router)
app.include_router(eegdata_router)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)
app.add_middleware(GZipMiddleware, minimum_size=1024)


@app.on_event("startup")
def start_log_queue() -> None:
    log_queue_listener.start()


@app.on_event("startup")
def check_database_up_to_date() -> None:
    if not check_database_is_up_to_date():
        app_logger.warning("database is not up-to-date, run alembic to upgrade")


@app.on_event("startup")
def init_db_data():
    with new_db_session() as db:
        create_root_user(db)
        create_default_experiment(db)
        init_default_human_subject_index(db)


@app.on_event("startup")
@repeat_task(config.DATABASE_HEARTBEAT_INTERVAL_SECONDS)
def database_heartbeat() -> None:
    with new_db_session() as db:
        send_heartbeat(db)


@app.on_event("shutdown")
def stop_log_queue() -> None:
    log_queue_listener.stop()


@app.middleware("http")
async def log_access_api(request: Request, call_next: Callable):
    start_time = datetime.now()
    request_id = generate_request_id()
    request_id_ctxvar.set(request_id)
    request.state.access_info = {"requestId": request_id, "method": request.method, "api": request.url.path}

    response = await call_next(request)

    rt = datetime.now() - start_time
    request.state.access_info.update(code=response.status_code, rt=int(rt.total_seconds() * 1000))
    log_message = ";".join(f"{key}={value}" for key, value in request.state.access_info.items())
    access_logger.info(log_message)

    return response


@app.middleware("http")
async def filter_blank_query_params(request: Request, call_next: Callable):
    """去除空的参数，避免非str的可选参数解析失败"""
    query_string_key = "query_string"
    latin_1_encoding = "latin-1"
    if (scope := request.scope) and scope.get(query_string_key):
        filtered_query_params = parse_qsl(qs=scope[query_string_key].decode(latin_1_encoding), keep_blank_values=False)
        scope[query_string_key] = urlencode(filtered_query_params).encode(latin_1_encoding)
    return await call_next(request)


@app.middleware("http")
async def get_content_language(request: Request, call_next: Callable):
    locale = request.headers.get("Content-Language", MessageLocale.zh_CN)
    if not any(locale == supported_locale for supported_locale in MessageLocale):
        locale = MessageLocale.zh_CN
    locale_ctxvar.set(locale)
    return await call_next(request)


@app.exception_handler(ServiceError)
def handle_service_error(_request: Request, e: ServiceError):
    return exception_response(e.status_code, e.code, e.message_id, *e.format_args)


@app.exception_handler(RequestValidationError)
def handle_request_validation_error(_request: Request, e: RequestValidationError):
    return exception_response(HTTP_400_BAD_REQUEST, ResponseCode.PARAMS_ERROR, "params error", repr(e))


@app.exception_handler(ExpiredSignatureError)
def handle_expired_token_exception(_request: Request, _e: ExpiredSignatureError):
    return exception_response(HTTP_401_UNAUTHORIZED, ResponseCode.SESSION_TIMEOUT, "session timeout")


@app.exception_handler(HTTPException)
@app.exception_handler(Exception)
def handle_unexpected_exception(_request: Request, e: Exception):
    return exception_response(HTTP_500_INTERNAL_SERVER_ERROR, ResponseCode.SERVER_ERROR, "inner server error", str(e))


def exception_response(status_code: int, response_code: int, message_id: str, *format_args: Any) -> ApiJsonResponse:
    message = translate_message(message_id, *format_args)
    return ApiJsonResponse(
        status_code=status_code, content=NoneResponse(code=response_code, message=message, data=None).dict()
    )


@app.get("/")
def index():
    if config.DEBUG_MODE:
        return RedirectResponse(url="/docs")
    else:
        raise ServiceError.page_not_found("/")


def create_default_experiment(db: Session) -> None:
    default_experiment = {
        "name": "DEFAULT",
        "description": "Default experiment for files without experiment",
        "type": ExperimentType.other,
        "location": "Nowhere",
        "start_at": datetime(year=2023, month=1, day=1, hour=0, minute=0, second=0),
        "end_at": datetime(year=2023, month=1, day=1, hour=0, minute=0, second=0),
        "main_operator": 1,
    }
    insert_or_update_experiment(db, 0, default_experiment)


def create_root_user(db: Session) -> None:
    root_user_create = UserCreate(
        username=ROOT_USERNAME,
        hashed_password=hash_password(ROOT_PASSWORD),
        staff_id=ROOT_USERNAME,
        access_level=AccessLevel.ADMINISTRATOR.value,
    )
    insert_or_update_user(db, root_user_create)


def init_default_human_subject_index(db: Session) -> None:
    if get_next_human_subject_index(db, update_index=False, exit_if_update_error=True) is None:
        insert_human_subject_index(db, 1)
