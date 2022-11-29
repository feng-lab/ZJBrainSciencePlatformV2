from typing import TypeVar

import ormar
from loguru import logger

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
async def list_users(offset: int, limit: int, include_deleted: bool) -> list[User]:
    query = User.objects.order_by("id")
    if not include_deleted:
        query = query.filter(is_deleted=False)
    users = await query.offset(offset).limit(limit).all()
    return users


@db_model_add_timezone
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
