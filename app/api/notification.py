from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.common.config import config
from app.common.context import Context, human_subject_context
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
def send_notification(
    request: NotificationBase, ctx: Context = Depends(human_subject_context)
) -> int:
    notification_create = NotificationCreate(
        **request.dict(), creator=ctx.user_id, status=Notification.Status.unread
    )
    notification_id = crud.insert_model(ctx.db, Notification, notification_create)
    return notification_id


@router.get("/api/getUnreadNotificationCount", description="获取未读通知总数", response_model=Response[int])
@wrap_api_response
def get_unread_notification_count(ctx: Context = Depends(human_subject_context)) -> int:
    unread_count = crud.get_notification_unread_count(ctx.db, ctx.user_id)
    return unread_count


@router.get(
    "/api/getRecentUnreadNotifications",
    description="获取最近未读通知",
    response_model=Response[list[NotificationResponse]],
)
@wrap_api_response
def get_recent_unread_notifications(
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
def get_notifications_by_page(
    notification_type: Notification.Type
    | None = Query(alias="type", description="通知类型", default=None),
    status: Notification.Status | None = Query(description="通知状态", default=None),
    create_time_start: datetime | None = Query(description="筛选通知发送时间的开始时间", default=None),
    create_time_end: datetime | None = Query(description="筛选通知发送时间的结束时间", default=None),
    page_param: GetModelsByPageParam = Depends(get_models_by_page),
    ctx: Context = Depends(human_subject_context),
) -> PagedData[NotificationResponse]:
    paged_data = crud.search_notifications(
        ctx.db,
        ctx.user_id,
        notification_type,
        status,
        create_time_start,
        create_time_end,
        page_param,
    )
    return paged_data


@router.post(
    "/api/markNotificationsAsRead", description="批量将通知标记为已读", response_model=Response[list[int]]
)
@wrap_api_response
def mark_notifications_as_read(
    request: MarkNotificationsAsReadRequest, ctx: Context = Depends(human_subject_context)
) -> list[int]:
    notification_ids = list(set(request.notification_ids))
    crud.update_notifications_as_read(ctx.db, ctx.user_id, request.is_all, notification_ids)
    return crud.list_unread_notifications(ctx.db, ctx.user_id, request.is_all, notification_ids)
