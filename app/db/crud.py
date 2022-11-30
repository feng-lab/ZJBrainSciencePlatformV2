import asyncio
from typing import TypeVar

import ormar
from loguru import logger
from ormar import QuerySet

from app.model.db_model import User, Notification
from app.utils import utc_now, db_model_add_timezone

DBModel = TypeVar("DBModel", bound=ormar.Model)


@db_model_add_timezone
async def update(model: DBModel, **updates) -> DBModel:
    if model is not None:
        updates["gmt_modified"] = utc_now()
        columns = list(updates.keys())
        model = await model.update(_columns=columns, **updates)
    return model


@db_model_add_timezone
async def create_user(user: User) -> User:
    user = await user.save()
    logger.info(f"created user, {user=}")
    return user


@db_model_add_timezone
async def get_user_by_id(user_id: int) -> User | None:
    user = await User.objects.get_or_none(id=user_id, is_deleted=False)
    return user


@db_model_add_timezone
async def get_user_by_username(username: str) -> User | None:
    user = await User.objects.get_or_none(username=username, is_deleted=False)
    return user


@db_model_add_timezone
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


async def update_user(user: int | User, **updates) -> User:
    if isinstance(user, int):
        user = await get_user_by_id(user)
    return await update(user, **updates)


@db_model_add_timezone
async def create_notification(msg: Notification) -> Notification:
    msg = await msg.save()
    logger.info(f"created message, {msg=}")
    return msg


@db_model_add_timezone
async def list_notifications(
    user_id: int, offset: int, limit: int
) -> list[Notification]:
    msgs = (
        await Notification.objects.filter(receiver=user_id, is_deleted=False)
        .order_by("-create_at")
        .offset(offset)
        .limit(limit)
        .all()
    )
    return msgs


@db_model_add_timezone
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
