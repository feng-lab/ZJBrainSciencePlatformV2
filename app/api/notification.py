from fastapi import APIRouter, Depends, Query

from app.api.auth import get_current_user_as_human_subject
from app.config import config
from app.db import crud
from app.model.db_model import User, Notification
from app.model.request import SendNotificationRequest, MarkNotificationsAsReadRequest
from app.model.response import (
    ListNotificationsResponse,
    SendNotificationResponse,
    MarkNotificationsAsReadResponse,
)
from app.timezone_util import convert_timezone_before_handle_request
from app.utils import custom_json_response

router = APIRouter()


@router.post(
    "/api/sendNotification", description="发送通知", response_model=SendNotificationResponse
)
async def send_notification(
    request: SendNotificationRequest,
    user: User = Depends(get_current_user_as_human_subject()),
):
    request = convert_timezone_before_handle_request(request)
    notification = Notification(**request.dict(), creator=user.id)
    notification = await crud.create_model(notification)
    return SendNotificationResponse(data=notification.id)


@router.get(
    "/api/getRecentUnreadNotifications",
    description="获取最近未读通知",
    response_model=ListNotificationsResponse,
)
@custom_json_response
async def get_recent_unread_notifications(
    user: User = Depends(get_current_user_as_human_subject()),
    count: int = Query(
        description="数量", default=config.GET_RECENT_NOTIFICATIONS_COUNT, ge=0
    ),
):
    user_id = user.id
    recent_notifications = await crud.list_notifications(user_id, offset=0, limit=count)
    return ListNotificationsResponse(data=recent_notifications)


@router.get(
    "/api/getNotificationsByPage",
    description="分页获取未读通知",
    response_model=ListNotificationsResponse,
)
@custom_json_response
async def get_notifications_by_page(
    user: User = Depends(get_current_user_as_human_subject()),
    offset: int = Query(description="分页起始位置", default=0, ge=0),
    limit: int = Query(
        description="分页大小", default=config.LIST_NOTIFICATIONS_LIMIT, ge=0
    ),
):
    user_id = user.id
    recent_notifications = await crud.list_notifications(user_id, offset, limit)
    return ListNotificationsResponse(data=recent_notifications)


@router.post(
    "/api/markNotificationsAsRead",
    description="批量将通知标记为已读",
    response_model=MarkNotificationsAsReadResponse,
)
async def mark_notifications_as_read(
    request: MarkNotificationsAsReadRequest,
    user: User = Depends(get_current_user_as_human_subject()),
):
    user_id = user.id
    notification_ids = set(request.notification_ids)
    msgs = await crud.list_unread_notifications(
        user_id, request.is_all, list(notification_ids)
    )
    if len(msgs) > 0:
        await crud.update_notifications_as_read(msgs)
    not_marked_notifications = [
        msg.id for msg in msgs if msg.id not in notification_ids
    ]
    return MarkNotificationsAsReadResponse(data=not_marked_notifications)
