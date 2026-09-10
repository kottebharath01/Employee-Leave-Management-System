from sqlalchemy.orm import Session

from app.core.enums import NotificationType
from app.models.notification import Notification
from app.utils.exceptions import NotFoundError, AuthorizationError


def create_notification(
    db: Session,
    recipient_id: int,
    notification_type: NotificationType,
    message: str,
    leave_request_id: int | None = None,
) -> Notification:
    notification = Notification(
        recipient_id=recipient_id,
        notification_type=notification_type,
        message=message,
        leave_request_id=leave_request_id,
        is_read=False,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def list_notifications_for_user(db: Session, user_id: int, unread_only: bool = False) -> list[Notification]:
    query = db.query(Notification).filter(Notification.recipient_id == user_id)
    if unread_only:
        query = query.filter(Notification.is_read.is_(False))
    return query.order_by(Notification.created_at.desc()).all()


def mark_notification_read(db: Session, user_id: int, notification_id: int) -> Notification:
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise NotFoundError(f"Notification with id {notification_id} not found.")
    if notification.recipient_id != user_id:
        raise AuthorizationError("You cannot mark another user's notification as read.")
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification
