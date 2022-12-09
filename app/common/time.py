"""
db -> (UTC none->current) -> backend -> (format) -> response
request -> (none->current) -> backend -> (current->UTC) -> db
"""

from datetime import datetime, timezone, tzinfo

from dateutil import tz

from app.common.config import config
from app.common.util import Model, modify_model_field_by_type

CURRENT_TIMEZONE: tzinfo = tz.gettz(config.TIMEZONE)


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


def utc_now() -> datetime:
    return datetime.now(tz=tz.UTC)


def now() -> datetime:
    return datetime.now(tz=CURRENT_TIMEZONE)
