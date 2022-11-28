from loguru import logger

from app.model.db_model import User, Notification
from app.utils import convert_timezone_to_cst, list_convert_timezone_to_cst, utc_now


async def create_user(user: User) -> User:
    user = await user.save()
    logger.info(f"created user, {user=}")
    return convert_timezone_to_cst(user)


async def get_user_by_id(user_id: int) -> User | None:
    user = await User.objects.get_or_none(id=user_id, is_deleted=False)
    return convert_timezone_to_cst(user)


async def get_user_by_username(username: str) -> User | None:
    user = await User.objects.get_or_none(username=username, is_deleted=False)
    return convert_timezone_to_cst(user)


async def list_users(offset: int, limit: int, include_deleted: bool) -> list[User]:
    query = User.objects.order_by("id")
    if not include_deleted:
        query = query.filter(is_deleted=False)
    users = await query.offset(offset).limit(limit).all()
    return list_convert_timezone_to_cst(users)


async def update_user(user: int | User, **updates) -> User:
    if isinstance(user, int):
        user = await get_user_by_id(user)

    if user is not None:
        user = await user.update(**updates, gmt_modified=utc_now())
    return convert_timezone_to_cst(user)


async def create_notification(msg: Notification) -> Notification:
    msg = await msg.save()
    logger.info(f"created message, {msg=}")
    return convert_timezone_to_cst(msg)


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
    return list_convert_timezone_to_cst(msgs)


async def list_unread_notifications(
    user_id: int, is_all: bool, msg_ids: list[int]
) -> list[Notification]:
    query = Notification.objects.filter(
        receiver=user_id, is_deleted=False, status=Notification.Status.UNREAD.value
    )
    if not is_all:
        query = query.filter(id__in=msg_ids)
    msgs = await query.all()
    return list_convert_timezone_to_cst(msgs)


async def update_notifications_as_read(msgs: list[Notification]) -> None:
    now = utc_now()
    for msg in msgs:
        msg.status = Notification.Status.READ.value
        msg.gmt_modified = now
    await Notification.objects.bulk_update(msgs, columns=["status", "gmt_modified"])
