from fastapi import APIRouter, Depends, Query

from app import crud
from app.config import get_config
from app.models import User, Message
from app.requests import SendMessageRequest
from app.responses import (
    GetRecentUnreadMessagesResponse,
    CODE_SUCCESS,
    SendMessageResponse,
)
from app.user import get_current_user

router = APIRouter()


@router.post("/api/sendMessage", description="发消息", response_model=SendMessageResponse)
async def send_message(
    request: SendMessageRequest, user: User = Depends(get_current_user)
):
    msg = Message(**request.dict(), creator=user.id)
    msg = await crud.create_message(msg)
    return {
        "code": CODE_SUCCESS,
        "message": "send message success",
        "data": msg.id,
    }


@router.get(
    "/api/getRecentUnreadMessages",
    description="获取未读消息",
    response_model=GetRecentUnreadMessagesResponse,
)
async def get_recent_unread_messages(
    user: User = Depends(get_current_user),
    count: int = Query(
        description="数量", default=get_config().GET_RECENT_MESSAGES_COUNT, ge=0
    ),
):
    user_id = user.id
    recent_msgs = await crud.list_recent_messages(user_id, count)
    return {
        "code": CODE_SUCCESS,
        "message": "get recent unread messages success",
        "data": recent_msgs,
    }
