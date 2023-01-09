import sys
from datetime import datetime
from logging import ERROR, INFO, Formatter, Handler, Logger, LogRecord, StreamHandler, getLogger
from logging.handlers import QueueHandler, QueueListener, TimedRotatingFileHandler
from pathlib import Path
from queue import Queue
from typing import Callable

from app.common.config import config
from app.common.util import CURRENT_TIMEZONE, get_module_name

ACCESS_LOGGER_NAME = "access"
UVICORN_LOGGER_NAME = "uvicorn.access"
SQLALCHEMY_LOGGER_NAME = "sqlalchemy.engine.Engine"
LOGGER_NAMES = {ACCESS_LOGGER_NAME, UVICORN_LOGGER_NAME, SQLALCHEMY_LOGGER_NAME}

DEFAULT_LOG_FORMAT = "%(asctime)s|%(levelname)s|%(module_name)s:%(lineno)d|%(message)s"
if config.DEBUG_MODE:
    DEFAULT_LOG_FORMAT = "%(asctime)s|%(levelname)s|%(name)s|%(module_name)s:%(lineno)d|%(message)s"
ACCESS_LOG_FORMAT = "%(asctime)s|%(levelname)s|%(message)s"


def current_time_tuple(_second, _what):
    return datetime.now(CURRENT_TIMEZONE).timetuple()


Formatter.converter = current_time_tuple


def init_handler(
    path: Path,
    *log_filters: Callable[[LogRecord], bool],
    level: int | None = None,
    log_format: str = DEFAULT_LOG_FORMAT,
) -> Handler:
    log_handler = TimedRotatingFileHandler(
        filename=path, when="D", backupCount=config.LOG_ROTATING_DAYS, encoding="UTF-8"
    )
    if level is not None:
        log_handler.setLevel(level)
    log_formatter = Formatter(fmt=log_format)
    log_handler.setFormatter(log_formatter)
    for log_filter in log_filters:
        log_handler.addFilter(log_filter)
    return log_handler


def root_logger_filter(record: LogRecord) -> bool:
    return record.name not in LOGGER_NAMES


def name_logger_filter(name: str) -> Callable[[LogRecord], bool]:
    def log_filter(record: LogRecord) -> bool:
        return record.name == name

    return log_filter


class CustomFormatQueueHandler(QueueHandler):
    def prepare(self, record: LogRecord) -> LogRecord:
        record.module_name = get_module_name(record.pathname)
        record.msg = record.msg.replace("\n", " ")
        return super().prepare(record)


root_handler = init_handler(config.LOG_ROOT / "app.log", root_logger_filter)
error_handler = init_handler(config.LOG_ROOT / "error.log", root_logger_filter, level=ERROR)
access_handler = init_handler(
    config.LOG_ROOT / "access.log",
    name_logger_filter(ACCESS_LOGGER_NAME),
    log_format=ACCESS_LOG_FORMAT,
)
uvicorn_handler = init_handler(
    config.LOG_ROOT / "uvicorn.log", name_logger_filter(UVICORN_LOGGER_NAME)
)
sqlalchemy_handler = init_handler(
    config.LOG_ROOT / "sqlalchemy.log", name_logger_filter(SQLALCHEMY_LOGGER_NAME), level=INFO
)

log_queue = Queue()
log_queue_handler = CustomFormatQueueHandler(log_queue)
log_queue_listener = QueueListener(log_queue, respect_handler_level=True)
handlers = [root_handler, access_handler, error_handler, uvicorn_handler, sqlalchemy_handler]
if config.DEBUG_MODE:
    stdout_handler = StreamHandler(sys.stdout)
    stdout_handler.setFormatter(Formatter(fmt=DEFAULT_LOG_FORMAT))
    handlers.append(stdout_handler)
log_queue_listener.handlers = tuple(handlers)


def init_logger(name: str | None, level: int = INFO) -> Logger:
    logger = getLogger(name)
    logger.setLevel(level)
    logger.propagate = False
    logger.handlers = [log_queue_handler]
    return logger


root_logger = init_logger(None)
access_logger = init_logger(ACCESS_LOGGER_NAME)
uvicorn_logger = init_logger(UVICORN_LOGGER_NAME)
sqlalchemy_logger = init_logger(SQLALCHEMY_LOGGER_NAME, level=INFO)
