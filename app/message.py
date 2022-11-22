from typing import Optional

from fastapi import APIRouter, Depends, Query

from app import crud
from app.config import get_config
from app.models import User, Message
from app.requests import SendMessageRequest
from app.responses import (
    ListMessagesResponse,
    SendMessageResponse,
    MarkMessagesAsReadResponse,
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


@router.post(
    "/api/markMessagesAsRead",
    description="批量将消息标记为已读",
    response_model=MarkMessagesAsReadResponse,
)
async def mark_messages_as_read(
    user: User = Depends(get_current_user),
    is_all: bool = Query(description="是否标记所有消息", default=False),
    message_ids: Optional[list[int]] = Query(
        alias="msg", description="消息ID，可以有多个", default=None
    ),
):
    user_id = user.id
    message_ids = set(message_ids) if message_ids else set()
    msgs = await crud.list_unread_messages(user_id, is_all, list(message_ids))
    if len(msgs) > 0:
        await crud.update_messages_as_read(msgs)
    not_marked_msgs = [msg.id for msg in msgs if msg.id not in message_ids]
    return MarkMessagesAsReadResponse(data=not_marked_msgs)
