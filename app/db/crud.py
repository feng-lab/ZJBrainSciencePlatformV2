import asyncio
import functools
import inspect
import itertools
import logging
import sys
from typing import Awaitable, Callable, TypeVar

import ormar
from ormar import QuerySet

from app.config import config
from app.model.db_model import Experiment, Notification, User
from app.model.request import GetExperimentsByPageSortBy, GetExperimentsByPageSortOrder
from app.timezone_util import convert_timezone_after_get_db, convert_timezone_before_save, utc_now
from app.util import get_module_defined_members

logger = logging.getLogger(__name__)

DBModel = TypeVar("DBModel", bound=ormar.Model, contravariant=True)


async def update_model(model: DBModel, **updates) -> DBModel:
    if model is not None:
        updates["gmt_modified"] = utc_now()
        columns = list(updates.keys())
        model = await model.update(_columns=columns, **updates)
    return model


async def create_model(model: DBModel) -> DBModel:
    model = convert_timezone_before_save(model)
    model = await model.save()
    logger.info(f"created model {type(model).__name__}: {repr(model)}")
    return model


async def get_model_by_id(model_type: type[DBModel], model_id: int) -> DBModel | None:
    model = await model_type.objects.get_or_none(id=model_id, is_deleted=False)
    return model


async def get_model(model_type: type[DBModel], **queries) -> DBModel | None:
    model = await model_type.objects.get_or_none(**queries, is_deleted=False)
    return model


async def get_user_by_username(username: str) -> User | None:
    return await get_model(User, username=username)


async def search_users(
    username: str | None,
    staff_id: str | None,
    access_level: int | None,
    offset: int,
    limit: int,
    include_deleted: bool,
) -> (int, list[User]):
    query: QuerySet = User.objects
    if username is not None:
        query = query.filter(username__icontains=username)
    if staff_id is not None:
        query = query.filter(staff_id__icontains=staff_id)
    if access_level is not None:
        query = query.filter(access_level=access_level)
    if not include_deleted:
        query = query.filter(is_deleted=False)

    total_count, users = await asyncio.gather(
        query.count(), query.offset(offset).limit(limit).order_by("id").all()
    )
    return total_count, users


async def list_notifications(user_id: int, offset: int, limit: int) -> list[Notification]:
    msgs = (
        await Notification.objects.filter(receiver=user_id, is_deleted=False)
        .order_by("-create_at")
        .offset(offset)
        .limit(limit)
        .all()
    )
    return msgs


async def list_unread_notifications(
    user_id: int, is_all: bool, msg_ids: list[int]
) -> list[Notification]:
    query = Notification.objects.filter(
        receiver=user_id, is_deleted=False, status=Notification.Status.UNREAD.value
    )
    if not is_all:
        query = query.filter(id__in=msg_ids)
    msgs = await query.all()
    return msgs


async def update_notifications_as_read(msgs: list[Notification]) -> None:
    now = utc_now()
    for msg in msgs:
        msg.status = Notification.Status.READ.value
        msg.gmt_modified = now
    await Notification.objects.bulk_update(msgs, columns=["status", "gmt_modified"])


async def search_experiments(
    search: str,
    sort_by: GetExperimentsByPageSortBy,
    sort_order: GetExperimentsByPageSortOrder,
    offset: int,
    limit: int,
    include_deleted: bool,
) -> list[Experiment]:
    query: QuerySet = Experiment.objects.offset(offset).limit(limit)

    if sort_by is GetExperimentsByPageSortBy.START_TIME:
        order_key = "start_at"
    elif sort_by is GetExperimentsByPageSortBy.TYPE:
        order_key = "type"
    else:
        raise ValueError("invalid sort_by")
    if sort_order is GetExperimentsByPageSortOrder.ASC:
        pass
    elif sort_order is GetExperimentsByPageSortOrder.DESC:
        order_key = "-" + order_key
    else:
        raise ValueError("invalid sort_order")
    query = query.order_by(order_key)
    if search:
        query = query.filter(name__icontains=search)
    if not include_deleted:
        query = query.filter(is_deleted=False)

    return await query.all()


def add_common_stuff() -> None:
    current_module = sys.modules[__name__]
    async_funcs = get_module_defined_members(
        current_module, lambda _name, item: inspect.iscoroutinefunction(item)
    )
    for name, func in async_funcs:
        new_func = convert_db_model_timezone(func)
        if config.DEBUG_MODE:
            new_func = log_db_operation(name, new_func)
        setattr(current_module, name, new_func)


def convert_db_model_timezone(func: Callable[..., Awaitable[DBModel | list[DBModel] | None]]):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> DBModel | list[DBModel] | None:
        result = await func(*args, **kwargs)
        if result is None:
            return None
        if isinstance(result, ormar.Model):
            return convert_timezone_after_get_db(result)
        if isinstance(result, list):
            return [
                convert_timezone_after_get_db(model) if isinstance(model, ormar.Model) else model
                for model in result
            ]
        return result

    return wrapper


def log_db_operation(name: str, func: Callable[..., Awaitable[...]]):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        func_sig = inspect.signature(func)
        real_args = ",".join(
            f"{param_name}={repr(param_value)}"
            for param_name, param_value in zip(
                func_sig.parameters.keys(), itertools.chain(args, kwargs)
            )
        )
        result = await func(*args, **kwargs)
        logger.info(f"{name}({real_args})->{repr(result)}")
        return result

    return wrapper


add_common_stuff()
