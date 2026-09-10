from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.employee import Employee
from app.schemas.misc import NotificationOut
from app.services import notification_service

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get("", response_model=list[NotificationOut])
def list_notifications_route(
    unread_only: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    return notification_service.list_notifications_for_user(db, current_user.id, unread_only=unread_only)


@router.patch("/{notification_id}/read", response_model=NotificationOut)
def mark_read_route(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    return notification_service.mark_notification_read(db, current_user.id, notification_id)
