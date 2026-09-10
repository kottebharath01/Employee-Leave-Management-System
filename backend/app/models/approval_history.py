from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, func, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import ApprovalAction
from app.database.session import Base


class ApprovalHistory(Base):
    """
    Immutable audit trail. A new row is inserted for every approval-related
    action; existing rows are never updated or deleted.
    """
    __tablename__ = "approval_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    leave_request_id: Mapped[int] = mapped_column(ForeignKey("leave_requests.id"), nullable=False, index=True)
    approver_id: Mapped[int | None] = mapped_column(ForeignKey("employees.id"), nullable=True)

    action: Mapped[str] = mapped_column(
        SAEnum(ApprovalAction, name="approval_action_enum", native_enum=False, length=20), nullable=False
    )
    reason: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    leave_request = relationship("LeaveRequest", back_populates="approval_history")
    approver = relationship("Employee")
