import functools
import socket
import sys
import threading
import time
from datetime import datetime, timezone, tzinfo
from pathlib import Path
from typing import TypeVar

from dateutil import tz
from pydantic import BaseModel

from app.common.config import config

Model = TypeVar("Model", bound=BaseModel)
AnotherModel = TypeVar("AnotherModel", bound=BaseModel)
T = TypeVar("T")

CURRENT_TIMEZONE: tzinfo = tz.gettz(config.TIMEZONE)

SYS_PATHS = []
for sys_path in {Path(path).absolute() for path in sys.path}:
    for i, added_path in enumerate(SYS_PATHS):
        if sys_path.is_relative_to(added_path):
            SYS_PATHS.insert(i, sys_path)
            break
    else:
        SYS_PATHS.append(sys_path)


@functools.lru_cache(maxsize=None)
def get_module_name(module_path: Path | str) -> str | None:
    module_path = Path(module_path).absolute()
    for path in SYS_PATHS:
        if module_path.is_relative_to(path):
            return ".".join(module_path.relative_to(path).parts).rstrip(".py")
    return None


def now() -> datetime:
    return datetime.now(tz=CURRENT_TIMEZONE)


def utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


CURRENT_MACHINE_ID: int | None = None
_machine_id_refresh_lock = threading.Lock()


def get_machine_id(refresh: bool = False) -> int:
    global CURRENT_MACHINE_ID
    if refresh or CURRENT_MACHINE_ID is None:
        with _machine_id_refresh_lock:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0)
            try:
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
            except Exception:
                ip = "127.0.0.1"
            finally:
                s.close()
            CURRENT_MACHINE_ID = convert_ip_2_machine_id(ip)
    return CURRENT_MACHINE_ID


def convert_ip_2_machine_id(ip: str) -> int:
    ip_parts = [int(part) for part in ip.split(".")]
    ip_int = ip_parts[3] + (ip_parts[2] << 8) + (ip_parts[1] << 16) + (ip_parts[0] << 24)
    return ip_int


class WrapCounter:
    MAX: int = 2**31 - 1

    def __init__(self):
        self._value: int = 0
        self._lock = threading.Lock()

    def get_value(self) -> int:
        with self._lock:
            if self._value < WrapCounter.MAX:
                self._value += 1
            else:
                self._value = 0
            return self._value


request_id_counter = WrapCounter()


def generate_request_id() -> str:
    timestamp = int(time.time_ns() / 1_000_000) & 0x1FFFFFFFFFF
    machine_id = get_machine_id() & 0x3FF
    serial_num = request_id_counter.get_value() & 0xFFF
    request_id = (timestamp << 22) + (machine_id << 12) + serial_num
    return f"{request_id:x}"
