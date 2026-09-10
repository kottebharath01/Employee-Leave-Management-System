from datetime import datetime, date

from pydantic import BaseModel, ConfigDict, field_validator


# ---------- Department ----------
class DepartmentCreate(BaseModel):
    name: str
    description: str | None = None


class DepartmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime


# ---------- Approval history ----------
class ApprovalHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    leave_request_id: int
    approver_id: int | None
    action: str
    reason: str | None
    timestamp: datetime


# ---------- Notifications ----------
class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    recipient_id: int
    notification_type: str
    message: str
    leave_request_id: int | None
    is_read: bool
    created_at: datetime


# ---------- Holidays ----------
class HolidayCreate(BaseModel):
    holiday_date: date
    name: str
    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Holiday name must not be empty")
        return v.strip()


class HolidayUpdate(BaseModel):
    holiday_date: date | None = None
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None


class HolidayOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    holiday_date: date
    name: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
