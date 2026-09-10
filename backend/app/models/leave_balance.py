from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class LeaveBalance(Base):
    """
    Tracks how many paid days of a given leave type an employee has left
    in the current year. One row per (employee, leave_type, year).
    """
    __tablename__ = "leave_balances"
    __table_args__ = (
        UniqueConstraint("employee_id", "leave_type_id", "year", name="uq_employee_leave_type_year"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False, index=True)
    leave_type_id: Mapped[int] = mapped_column(ForeignKey("leave_types.id"), nullable=False, index=True)
    year: Mapped[int] = mapped_column(nullable=False)

    total_days: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False, default=0)
    used_days: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    employee = relationship("Employee", back_populates="leave_balances")
    leave_type = relationship("LeaveType", back_populates="balances")

    @property
    def available_days(self) -> float:
        return float(self.total_days) - float(self.used_days)
