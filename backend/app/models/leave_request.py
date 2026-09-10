from datetime import datetime, date

from sqlalchemy import String, DateTime, Date, ForeignKey, Numeric, func, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import LeaveRequestStatus
from app.database.session import Base


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False, index=True)
    leave_type_id: Mapped[int] = mapped_column(ForeignKey("leave_types.id"), nullable=False, index=True)

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    explanation: Mapped[str] = mapped_column(String(1000), nullable=False)

    status: Mapped[str] = mapped_column(
        SAEnum(LeaveRequestStatus, name="leave_status_enum", native_enum=False, length=20),
        nullable=False,
        default=LeaveRequestStatus.PENDING,
        index=True,
    )

    paid_days: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False, default=0)
    unpaid_days: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False, default=0)

    # The employee currently assigned to approve/reject this request.
    # Null once the request is CEO-auto-approved (no approver needed).
    current_approver_id: Mapped[int | None] = mapped_column(ForeignKey("employees.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    employee = relationship("Employee", back_populates="leave_requests", foreign_keys=[employee_id])
    current_approver = relationship("Employee", foreign_keys=[current_approver_id])
    leave_type = relationship("LeaveType", back_populates="leave_requests")
    approval_history = relationship(
        "ApprovalHistory", back_populates="leave_request", order_by="ApprovalHistory.timestamp"
    )

    @property
    def total_days(self) -> float:
        return float(self.paid_days) + float(self.unpaid_days)
