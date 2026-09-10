from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, ForeignKey, func, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import NotificationType
from app.database.session import Base


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    recipient_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False, index=True)
    notification_type: Mapped[str] = mapped_column(
        SAEnum(NotificationType, name="notification_type_enum", native_enum=False, length=40), nullable=False
    )
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    leave_request_id: Mapped[int | None] = mapped_column(ForeignKey("leave_requests.id"), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    recipient = relationship("Employee")
    leave_request = relationship("LeaveRequest")
