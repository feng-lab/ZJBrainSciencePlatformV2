import logging
import sys
from datetime import datetime
from http import HTTPStatus
from typing import Callable
from urllib.parse import parse_qsl, urlencode

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from jose import ExpiredSignatureError
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.responses import RedirectResponse
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from app.api import experiment, user
from app.api.algorithm import router as algorithm_router
from app.api.auth import router as auth_router
from app.api.experiment import router as experiment_router
from app.api.file import router as file_router
from app.api.notification import router as notification_router
from app.api.paradigm import router as paradigm_router
from app.api.user import router as user_router
from app.common.config import config
from app.common.exception import ServiceError
from app.common.log import ACCESS_LOGGER_NAME, log_queue_listener
from app.db import check_database_is_up_to_date
from app.model.response import CODE_FAIL, CODE_SESSION_TIMEOUT, NoneResponse

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
    ],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(notification_router)
app.include_router(experiment_router)
app.include_router(file_router)
app.include_router(paradigm_router)
app.include_router(algorithm_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1024)


@app.on_event("startup")
def startup() -> None:
    log_queue_listener.start()
    if not check_database_is_up_to_date():
        app_logger.error("database is not up-to-date, run alembic to upgrade")
        sys.exit(1)
    user.create_root_user()
    experiment.create_default_experiment()


@app.on_event("shutdown")
def shutdown() -> None:
    log_queue_listener.stop()


@app.middleware("http")
async def log_access_api(request: Request, call_next: Callable):
    start_time = datetime.now()
    request.state.access_info = {"method": request.method, "api": request.url.path}

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
        filtered_query_params = parse_qsl(
            qs=scope[query_string_key].decode(latin_1_encoding), keep_blank_values=False
        )
        scope[query_string_key] = urlencode(filtered_query_params).encode(latin_1_encoding)
    return await call_next(request)


@app.exception_handler(HTTPException)
def handle_http_exception(_request: Request, e: HTTPException):
    return JSONResponse(
        status_code=e.status_code, content=NoneResponse(code=CODE_FAIL, message=e.detail).dict()
    )


@app.exception_handler(ServiceError)
def handle_service_error(_request: Request, e: ServiceError):
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content=NoneResponse(code=e.code, message=e.message).dict(),
    )


@app.exception_handler(RequestValidationError)
def handle_http_exception(_request: Request, e: RequestValidationError):
    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content=NoneResponse(code=CODE_FAIL, message=repr(e)).dict(),
    )


@app.exception_handler(ExpiredSignatureError)
def handle_expired_token_exception(_request: Request, _e: ExpiredSignatureError):
    return JSONResponse(
        status_code=HTTP_401_UNAUTHORIZED,
        content=NoneResponse(code=CODE_SESSION_TIMEOUT, message="session timeout").dict(),
    )


@app.get("/")
def index():
    if config.DEBUG_MODE:
        return RedirectResponse(url="/docs")
    else:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
