from fastapi import APIRouter, Depends, Query

from app.api.auth import get_current_user_as_human_subject
from app.config import config
from app.db import crud
from app.model.db_model import Notification, User
from app.model.request import MarkNotificationsAsReadRequest, SendNotificationRequest
from app.model.response import NotificationInfo, Response, wrap_api_response
from app.timezone_util import convert_timezone_before_handle_request
from app.util import convert_models

router = APIRouter(tags=["notification"])


@router.post("/api/sendNotification", description="发送通知", response_model=Response[int])
@wrap_api_response
async def send_notification(
    request: SendNotificationRequest, user: User = Depends(get_current_user_as_human_subject())
) -> int:
    request = convert_timezone_before_handle_request(request)
    notification = Notification(**request.dict(), creator=user.id)
    notification = await crud.create_model(notification)
    return notification.id


@router.get(
    "/api/getRecentUnreadNotifications",
    description="获取最近未读通知",
    response_model=Response[list[NotificationInfo]],
)
@wrap_api_response
async def get_recent_unread_notifications(
    user: User = Depends(get_current_user_as_human_subject()),
    count: int = Query(description="数量", default=config.GET_RECENT_NOTIFICATIONS_COUNT, ge=0),
) -> list[NotificationInfo]:
    user_id = user.id
    recent_notifications = await crud.list_notifications(user_id, offset=0, limit=count)
    return convert_models(recent_notifications, NotificationInfo)


@router.get(
    "/api/getNotificationsByPage",
    description="分页获取未读通知",
    response_model=Response[list[NotificationInfo]],
)
@wrap_api_response
async def get_notifications_by_page(
    user: User = Depends(get_current_user_as_human_subject()),
    offset: int = Query(description="分页起始位置", default=0, ge=0),
    limit: int = Query(description="分页大小", default=config.LIST_NOTIFICATIONS_LIMIT, ge=0),
) -> list[NotificationInfo]:
    user_id = user.id
    recent_notifications = await crud.list_notifications(user_id, offset, limit)
    return convert_models(recent_notifications, NotificationInfo)


@router.post(
    "/api/markNotificationsAsRead", description="批量将通知标记为已读", response_model=Response[list[int]]
)
@wrap_api_response
async def mark_notifications_as_read(
    request: MarkNotificationsAsReadRequest,
    user: User = Depends(get_current_user_as_human_subject()),
) -> list[int]:
    user_id = user.id
    notification_ids = set(request.notification_ids)
    msgs = await crud.list_unread_notifications(user_id, request.is_all, list(notification_ids))
    if len(msgs) > 0:
        await crud.update_notifications_as_read(msgs)
    not_marked_notifications = [msg.id for msg in msgs if msg.id not in notification_ids]
    return not_marked_notifications
