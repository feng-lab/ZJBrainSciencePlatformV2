from fastapi import APIRouter, Depends, Query

from app import crud
from app.config import get_config
from app.models import User, Message
from app.requests import SendMessageRequest
from app.responses import (
    ListMessagesResponse,
    SendMessageResponse,
)
from app.user import get_current_user

router = APIRouter()


@router.post("/api/sendMessage", description="发消息", response_model=SendMessageResponse)
async def send_message(
    request: SendMessageRequest, user: User = Depends(get_current_user)
):
    msg_create = Message(**request.dict(), creator=user.id)
    msg = await crud.create_message(msg_create)
    return SendMessageResponse(data=msg.id)


@router.get(
    "/api/getRecentUnreadMessages",
    description="获取未读消息",
    response_model=ListMessagesResponse,
)
async def get_recent_unread_messages(
    user: User = Depends(get_current_user),
    count: int = Query(
        description="数量", default=get_config().GET_RECENT_MESSAGES_COUNT, ge=0
    ),
):
    user_id = user.id
    recent_msgs = await crud.list_messages(user_id, offset=0, limit=count)
    return ListMessagesResponse(data=recent_msgs)


@router.get(
    "/api/getMessagesByPage",
    description="获取未读消息",
    response_model=ListMessagesResponse,
)
async def get_messages_by_page(
    user: User = Depends(get_current_user),
    offset: int = Query(description="分页起始位置", default=0, ge=0),
    limit: int = Query(
        description="分页大小", default=get_config().LIST_MESSAGES_LIMIT, ge=0
    ),
):
    user_id = user.id
    recent_msgs = await crud.list_messages(user_id, offset, limit)
    return ListMessagesResponse(data=recent_msgs)
