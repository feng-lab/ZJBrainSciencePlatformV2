from objprint import op

from .models import User
from .requests import CreateUserRequest


async def create_user(request: CreateUserRequest, hashed_password: str) -> None:
    new_user = await User.objects.create(
        username=request.username,
        hashed_password=hashed_password,
        staff_id=request.staff_id,
        account_type=request.account_type,
    )
    op(new_user)


async def get_user_by_username(username: str) -> User:
    return await User.objects.get_or_none(username=username, is_deleted=False)
