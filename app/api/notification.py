from fastapi import APIRouter, Depends, Query

from app.common.config import config
from app.common.context import Context, human_subject_context
from app.common.time import convert_timezone_before_handle_request
from app.db import crud
from app.db.orm import Notification
from app.model.request import (
    GetModelsByPageParam,
    MarkNotificationsAsReadRequest,
    get_models_by_page,
)
from app.model.response import PagedData, Response, wrap_api_response
from app.model.schema import NotificationBase, NotificationCreate, NotificationResponse

router = APIRouter(tags=["notification"])


@router.post("/api/sendNotification", description="发送通知", response_model=Response[int])
@wrap_api_response
async def send_notification(
    request: NotificationBase, ctx: Context = Depends(human_subject_context)
) -> int:
    request = convert_timezone_before_handle_request(request)
    notification_create = NotificationCreate(
        **request.dict(), creator=ctx.user_id, status=Notification.Status.unread
    )
    notification_id = crud.insert_model(ctx.db, Notification, notification_create)
    return notification_id


@router.get(
    "/api/getRecentUnreadNotifications",
    description="获取最近未读通知",
    response_model=Response[list[NotificationResponse]],
)
@wrap_api_response
async def get_recent_unread_notifications(
    count: int = Query(description="数量", default=config.GET_RECENT_NOTIFICATIONS_COUNT, ge=0),
    ctx: Context = Depends(human_subject_context),
) -> list[NotificationResponse]:
    page_param = GetModelsByPageParam(offset=0, limit=count, include_deleted=False)
    return crud.list_notifications(ctx.db, ctx.user_id, Notification.Status.unread, page_param)


@router.get(
    "/api/getNotificationsByPage",
    description="分页获取所有通知",
    response_model=Response[PagedData[NotificationResponse]],
)
@wrap_api_response
async def get_notifications_by_page(
    paging_param: GetModelsByPageParam = Depends(get_models_by_page),
    ctx: Context = Depends(human_subject_context),
) -> PagedData[NotificationResponse]:
    return crud.search_notifications(ctx.db, ctx.user_id, None, paging_param)


@router.post(
    "/api/markNotificationsAsRead", description="批量将通知标记为已读", response_model=Response[list[int]]
)
@wrap_api_response
async def mark_notifications_as_read(
    request: MarkNotificationsAsReadRequest, ctx: Context = Depends(human_subject_context)
) -> list[int]:
    notification_ids = list(set(request.notification_ids))
    crud.update_notifications_as_read(ctx.db, ctx.user_id, request.is_all, notification_ids)
    return crud.list_unread_notifications(ctx.db, ctx.user_id, request.is_all, notification_ids)
