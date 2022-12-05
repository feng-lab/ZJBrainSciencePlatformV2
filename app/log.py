import logging
from datetime import datetime
from logging import ERROR, INFO, Formatter, Handler, Logger, LogRecord, getLogger
from logging.handlers import QueueHandler, QueueListener, TimedRotatingFileHandler
from pathlib import Path
from queue import Queue
from typing import Callable

from app.config import config
from app.timezone_util import current_timezone

ACCESS_LOGGER_NAME = "access"
UVICORN_LOGGER_NAME = "uvicorn.access"
LOGGER_NAMES = {ACCESS_LOGGER_NAME, UVICORN_LOGGER_NAME}

DEFAULT_LOG_FORMAT = "%(asctime)s|%(levelname)s|%(pathname)s:%(lineno)d|%(message)s"
ACCESS_LOG_FORMAT = "%(asctime)s|%(levelname)s|%(message)s"


def current_time_tuple(_second, _what):
    return datetime.now(current_timezone).timetuple()


logging.Formatter.converter = current_time_tuple


def init_handler(
    path: Path,
    log_filter: Callable[[LogRecord], bool],
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
    log_handler.addFilter(log_filter)
    return log_handler


def root_logger_filter(record: LogRecord) -> bool:
    return record.name not in LOGGER_NAMES


def name_logger_filter(name: str) -> Callable[[LogRecord], bool]:
    def log_filter(record: LogRecord) -> bool:
        return record.name == name

    return log_filter


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

log_queue = Queue()
log_queue_handler = QueueHandler(log_queue)
log_queue_listener = QueueListener(
    log_queue,
    root_handler,
    access_handler,
    error_handler,
    uvicorn_handler,
    respect_handler_level=True,
)


def init_logger(name: str | None, level: int = INFO, log_handler: Handler | None = None) -> Logger:
    logger = getLogger(name)
    logger.setLevel(level)
    if log_handler is None:
        logger.addHandler(log_queue_handler)
    return logger


root_logger = init_logger(None)
access_logger = init_logger(ACCESS_LOGGER_NAME)
uvicorn_logger = init_logger(UVICORN_LOGGER_NAME)
