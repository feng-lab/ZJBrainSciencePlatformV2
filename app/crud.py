from datetime import datetime

from loguru import logger

from .models import User


async def create_user(user: User) -> None:
    await user.save()
    logger.info(f"created user, {user=}")


async def get_user_by_id(user_id: int) -> User | None:
    user = await User.objects.get_or_none(id=user_id, is_deleted=False)
    return user


async def get_user_by_username(username: str) -> User | None:
    user = await User.objects.get_or_none(username=username, is_deleted=False)
    return user


async def list_users(offset: int, limit: int, include_deleted: bool) -> list[User]:
    query = User.objects.order_by("id")
    if not include_deleted:
        query = query.filter(is_deleted=False)
    users = await query.offset(offset).limit(limit).all()
    return users


async def update_user(user: int | User, **updates) -> User:
    if isinstance(user, int):
        user = await get_user_by_id(user)

    if user is not None:
        utcnow = datetime.utcnow()
        user = await user.update(**updates, gmt_modified=utcnow)
    return user
