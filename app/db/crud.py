import asyncio
import functools
import inspect
import itertools
import logging
import sys
from typing import Any, Awaitable, Callable, TypeVar

import ormar
from ormar import QuerySet

from app.config import config
from app.model.db_model import Experiment, File, Notification, Paradigm, User
from app.model.request import (
    GetExperimentsByPageSortBy,
    GetExperimentsByPageSortOrder,
    GetModelsByPageParam,
)
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


async def bulk_update_models(models: list[DBModel], **updates) -> None:
    now = utc_now()
    for model in models:
        updates["gmt_modified"] = now
        model.update_from_dict(updates)
    columns = list(updates.keys())
    columns.append("gmt_modified")
    await Notification.objects.bulk_update(models, columns=columns)


async def create_model(model: DBModel) -> DBModel:
    model = convert_timezone_before_save(model)
    model = await model.save()
    logger.info(f"created model {type(model).__name__}: {repr(model)}")
    return model


async def bulk_create_models(models: list[DBModel]) -> None:
    model_type = type(models[0])
    await model_type.objects.bulk_create(models)


async def get_model_by_id(model_type: type[DBModel], model_id: int) -> DBModel | None:
    model = await model_type.objects.get_or_none(id=model_id, is_deleted=False)
    return model


async def get_model(model_type: type[DBModel], **queries) -> DBModel | None:
    model = await model_type.objects.get_or_none(**queries, is_deleted=False)
    return model


async def model_exists(model_type: type[DBModel], model_id: int) -> bool:
    exists = await model_type.objects.filter(id=model_id, is_deleted=False).exists()
    return exists


async def search_models(model_type: type[DBModel], **queries) -> list[DBModel]:
    models = await model_type.objects.filter(**queries, is_deleted=False).all()
    return models


# noinspection PyTypeChecker
async def bulk_search_models_by_key(
    model_type: type[DBModel], keys: list[Any], key_name: str
) -> list[list[DBModel]]:
    tasks = [
        model_type.objects.filter(**{key_name: key, "is_deleted": False}).all() for key in keys
    ]
    result = await asyncio.gather(*tasks)
    return result


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


# noinspection PyTypeChecker
async def bulk_get_username_by_id(user_ids: list[int]) -> list[str]:
    queries = [User.objects.get_or_none(id=user_id, is_deleted=False) for user_id in user_ids]
    users: list[User] = await asyncio.gather(*queries)
    return [user.username if user is not None else "" for user in users]


async def list_notifications(
    user_id: int, offset: int, limit: int, include_deleted: bool
) -> (int, list[Notification]):
    query = Notification.objects.filter(receiver=user_id)
    if not include_deleted:
        query = query.filter(is_deleted=False)
    total_count, notifications = await asyncio.gather(
        query.count(), query.order_by("-gmt_create").offset(offset).limit(limit).all()
    )
    return total_count, notifications


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


async def get_last_index_file(experiment_id: int) -> File | None:
    last_index_file = (
        await File.objects.filter(experiment_id=experiment_id, is_deleted=False)
        .order_by("-index")
        .limit(1)
        .get_or_none()
    )
    return last_index_file


async def get_file_extensions(experiment_id: int) -> list[str]:
    extensions = await File.objects.filter(
        experiment_id=experiment_id, is_deleted=False
    ).values_list(fields={"extension"}, flatten=True)

    return list(set(extensions))


async def search_files(
    experiment_id: int, path: str, extension: str, paging_param: GetModelsByPageParam
) -> list[File]:
    query: QuerySet = File.objects.filter(experiment_id=experiment_id)
    if path:
        query = query.filter(path__icontains=path)
    if extension:
        query = query.filter(extension__icontains=extension)
    if not paging_param.include_deleted:
        query = query.filter(is_deleted=False)
    files = await query.offset(paging_param.offset).limit(paging_param.limit).all()
    return files


async def search_paradigms(
    experiment_id: int, paging_param: GetModelsByPageParam
) -> list[Paradigm]:
    query: QuerySet = Paradigm.objects.filter(experiment_id=experiment_id)
    if not paging_param.include_deleted:
        query = query.filter(is_deleted=False)
    paradigms = await query.offset(paging_param.offset).limit(paging_param.limit).all()
    return paradigms


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
