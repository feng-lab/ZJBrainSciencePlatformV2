from fastapi import APIRouter, Depends, Query

import app.db.crud.notification as crud
from app.api import wrap_api_response
from app.common.config import config
from app.common.context import HumanSubjectContext
from app.common.exception import ServiceError
from app.db import common_crud
from app.db.orm import Notification
from app.model import convert
from app.model.enum_filed import NotificationStatus
from app.model.request import MarkNotificationsAsReadRequest
from app.model.response import Page, Response
from app.model.schema import NotificationBase, NotificationCreate, NotificationResponse, NotificationSearch

router = APIRouter(tags=["notification"])


@router.post("/api/sendNotification", description="发送通知", response_model=Response[int])
@wrap_api_response
def send_notification(request: NotificationBase, ctx: HumanSubjectContext = Depends()) -> int:
    notification_create = NotificationCreate(**request.dict(), creator=ctx.user_id, status=NotificationStatus.unread)
    notification_id = common_crud.insert_row(ctx.db, Notification, notification_create.dict(), commit=True)
    if notification_id is None:
        raise ServiceError.database_fail()
    return notification_id


@router.get("/api/getUnreadNotificationCount", description="获取未读通知总数", response_model=Response[int])
@wrap_api_response
def get_unread_notification_count(ctx: HumanSubjectContext = Depends()) -> int:
    unread_count = crud.get_notification_unread_count(ctx.db, ctx.user_id)
    return unread_count


@router.get(
    "/api/getRecentUnreadNotifications", description="获取最近未读通知", response_model=Response[list[NotificationResponse]]
)
@wrap_api_response
def get_recent_unread_notifications(
    count: int = Query(description="数量", default=config.GET_RECENT_NOTIFICATIONS_COUNT, ge=0),
    ctx: HumanSubjectContext = Depends(),
) -> list[NotificationResponse]:
    orm_notifications = crud.list_recent_unread_notifications(ctx.db, ctx.user_id, count)
    return convert.map_list(convert.notification_orm_2_response, orm_notifications)


@router.get("/api/getNotificationsByPage", description="分页获取所有通知", response_model=Response[Page[NotificationResponse]])
@wrap_api_response
def get_notifications_by_page(
    search: NotificationSearch = Depends(), ctx: HumanSubjectContext = Depends()
) -> Page[NotificationResponse]:
    total, orm_notifications = crud.search_notifications(ctx.db, search, ctx.user_id)
    notification_responses = convert.map_list(convert.notification_orm_2_response, orm_notifications)
    return Page(total=total, items=notification_responses)


@router.post("/api/markNotificationsAsRead", description="批量将通知标记为已读", response_model=Response[list[int]])
@wrap_api_response
def mark_notifications_as_read(
    request: MarkNotificationsAsReadRequest, ctx: HumanSubjectContext = Depends()
) -> list[int]:
    notification_ids = list(set(request.notification_ids))
    where = [
        Notification.receiver == ctx.user_id,
        Notification.is_deleted == False,
        Notification.status == NotificationStatus.unread,
    ]
    if not request.is_all:
        where.append(Notification.id.in_(notification_ids))
    success = common_crud.bulk_update_rows(
        ctx.db, Notification, where, {"status": NotificationStatus.read}, commit=True
    )
    if not success:
        raise ServiceError.database_fail()
    return crud.list_unread_notification_ids(ctx.db, ctx.user_id, request.is_all, notification_ids)
