from loguru import logger

from .models import User
from .requests import CreateUserRequest


async def create_user(request: CreateUserRequest, hashed_password: str) -> None:
    new_user = await User.objects.create(
        username=request.username,
        hashed_password=hashed_password,
        staff_id=request.staff_id,
        account_type=request.account_type,
    )
    logger.info(f"created user, {new_user=}")


async def get_user_by_id(user_id: int) -> User | None:
    user = await User.objects.get_or_none(id=user_id, is_deleted=False)
    return user


async def get_user_by_username(username: str) -> User | None:
    user = await User.objects.get_or_none(username=username, is_deleted=False)
    return user
