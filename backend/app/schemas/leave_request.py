from datetime import datetime, date

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class LeaveRequestPreviewIn(BaseModel):
    """Used by the 'preview before submit' endpoint (paid/unpaid split check)."""
    leave_type_id: int
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date cannot be before start_date")
        return self


class LeaveRequestPreviewOut(BaseModel):
    working_days: int
    available_paid_days: float
    paid_days: float
    unpaid_days: float
    requires_confirmation: bool
    message: str


class LeaveRequestCreate(BaseModel):
    leave_type_id: int
    start_date: date
    end_date: date
    explanation: str
    confirm_unpaid: bool = False  # must be True if request will include unpaid days

    @field_validator("explanation")
    @classmethod
    def validate_explanation(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("explanation must not be empty")
        return v.strip()

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date cannot be before start_date")
        return self


class LeaveRequestUpdate(BaseModel):
    """Only allowed while status == PENDING."""
    leave_type_id: int | None = None
    start_date: date | None = None
    end_date: date | None = None
    explanation: str | None = None
    confirm_unpaid: bool = False


class LeaveRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    leave_type_id: int
    start_date: date
    end_date: date
    explanation: str
    status: str
    paid_days: float
    unpaid_days: float
    current_approver_id: int | None
    created_at: datetime
    updated_at: datetime


class ApprovalActionIn(BaseModel):
    reason: str | None = None
