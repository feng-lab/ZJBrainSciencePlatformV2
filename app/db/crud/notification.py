from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session, immediateload

from app.db.crud import query_pages
from app.db.orm import Notification, User
from app.model.enum_filed import NotificationStatus
from app.model.schema import NotificationSearch


def get_notification_unread_count(db: Session, user_id: int) -> int:
    # noinspection PyTypeChecker
    stmt = select(func.count(Notification.id)).where(
        Notification.receiver == user_id,
        Notification.status == NotificationStatus.unread,
        Notification.is_deleted == False,
    )
    return db.execute(stmt).scalar()


def search_notifications(db: Session, search: NotificationSearch, user_id: int) -> tuple[int, Sequence[Notification]]:
    stmt = (
        select(Notification)
        .options(immediateload(Notification.creator_user).load_only(User.username))
        .where(Notification.receiver == user_id)
        .order_by(Notification.gmt_create.desc())
    )
    if search.notification_type:
        stmt = stmt.where(Notification.type == search.notification_type)
    if search.status:
        stmt = stmt.where(Notification.status == search.status)
    if search.create_time_start:
        stmt = stmt.where(Notification.gmt_create >= search.create_time_start)
    if search.create_time_end:
        stmt = stmt.where(Notification.gmt_create <= search.create_time_end)
    if not search.include_deleted:
        stmt = stmt.where(Notification.is_deleted == False)
    return query_pages(db, stmt, search.offset, search.limit)


def list_recent_unread_notifications(db: Session, user_id: int, count: int) -> Sequence[Notification]:
    stmt = (
        select(Notification)
        .options(immediateload(Notification.creator_user).load_only(User.username))
        .where(Notification.receiver == user_id, Notification.status == NotificationStatus.unread)
        .limit(count)
        .order_by(Notification.gmt_create.desc())
    )
    notifications = db.execute(stmt).scalars().all()
    return notifications


def list_unread_notification_ids(db: Session, user_id: int, is_all: bool, msg_ids: list[int]) -> list[int]:
    stmt = select(Notification.id).where(
        Notification.receiver == user_id,
        Notification.is_deleted == False,
        Notification.status == NotificationStatus.unread,
    )
    if not is_all:
        stmt = stmt.where(Notification.id.in_(msg_ids))
    unread_notification_ids = db.execute(stmt).scalars().all()
    return list(unread_notification_ids)
