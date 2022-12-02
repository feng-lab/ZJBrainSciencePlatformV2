# db -> (UTC none->current) -> backend -> (format) -> response
# request -> (none->current) -> backend -> (current->UTC) -> db
import functools
from datetime import datetime, timezone, tzinfo, timedelta
from typing import Callable

from dateutil.tz import gettz
from pydantic import BaseModel

from app.utils import modify_model_field_by_type
from app.config import config
from app.utils import Model

CURRENT_TIMEZONE: tzinfo = gettz(config.TIMEZONE)

UTC_OFFSET: timedelta = datetime.now(tz=timezone.utc).utcoffset()
CURRENT_TIMEZONE_OFFSET: timedelta = datetime.now(tz=CURRENT_TIMEZONE).utcoffset()


def convert_timezone(dt: datetime, from_tz: tzinfo, to_tz: tzinfo) -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=from_tz)
    return dt.astimezone(to_tz)


def convert_timezone_before_save(model: Model):
    return modify_model_field_by_type(
        model, datetime, lambda dt: convert_timezone(dt, CURRENT_TIMEZONE, timezone.utc)
    )


def convert_timezone_after_get_db(model: Model):
    return modify_model_field_by_type(
        model, datetime, lambda dt: convert_timezone(dt, timezone.utc, CURRENT_TIMEZONE)
    )


def convert_timezone_before_handle_request(model: Model):
    return modify_model_field_by_type(
        model, datetime, lambda dt: dt.replace(tzinfo=CURRENT_TIMEZONE)
    )


def convert_db_model_timezone(func: Callable[..., Model | list[Model]]):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Model | list[Model] | None:
        result = await func(*args, **kwargs)
        if result is None:
            return None
        if isinstance(result, BaseModel):
            return convert_timezone_after_get_db(result)
        if isinstance(result, list):
            return [
                convert_timezone_after_get_db(model)
                if isinstance(model, BaseModel)
                else model
                for model in result
            ]
        return result

    return wrapper
