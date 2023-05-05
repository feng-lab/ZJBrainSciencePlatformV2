from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.crud import SearchModel
from app.db.orm import Notification, User
from app.model.enum_filed import NotificationStatus, NotificationType
from app.model.response import Page
from app.model.schema import NotificationInDB, NotificationResponse, PageParm


def get_notification_unread_count(db: Session, user_id: int) -> int:
    # noinspection PyTypeChecker
    stmt = select(func.count(Notification.id)).where(
        Notification.receiver == user_id,
        Notification.status == NotificationStatus.unread,
        Notification.is_deleted == False,
    )
    return db.execute(stmt).scalar()


def build_search_notification(db: Session) -> SearchModel:
    return (
        SearchModel(db, Notification)
        .select(Notification, User.username)
        .join(User, Notification.receiver == User.id)
        .map_model_with(
            lambda row: NotificationResponse(
                **NotificationInDB.from_orm(row[0]).dict(), creator_name=row[1]
            )
        )
    )


def search_notifications(
    db: Session,
    user_id: int,
    notification_type: NotificationType | None,
    status: NotificationStatus | None,
    create_time_start: datetime | None,
    create_time_end: datetime | None,
    page_param: PageParm,
) -> Page[NotificationResponse]:
    return (
        build_search_notification(db)
        .page_param(page_param)
        .where_eq(Notification.receiver, user_id)
        .where_eq(Notification.type, notification_type)
        .where_eq(Notification.status, status)
        .where_ge(Notification.gmt_create, create_time_start)
        .where_le(Notification.gmt_create, create_time_end)
        .order_by(Notification.gmt_create.desc())
        .paged_data(NotificationResponse)
    )


def list_notifications(
    db: Session, user_id: int, status: NotificationStatus | None, page_param: PageParm
) -> list[NotificationResponse]:
    return (
        build_search_notification(db)
        .page_param(page_param)
        .where_eq(Notification.receiver, user_id)
        .where_eq(Notification.status, status)
        .order_by(Notification.gmt_create.desc())
        .items(NotificationResponse)
    )


def list_unread_notifications(
    db: Session, user_id: int, is_all: bool, msg_ids: list[int]
) -> list[int]:
    # noinspection PyTypeChecker
    stmt = select(Notification.id).where(
        Notification.receiver == user_id,
        Notification.is_deleted == False,
        Notification.status == NotificationStatus.unread,
    )
    if not is_all:
        stmt = stmt.where(Notification.id.in_(msg_ids))
    unread_notification_ids = db.execute(stmt).scalars().all()
    return list(unread_notification_ids)
