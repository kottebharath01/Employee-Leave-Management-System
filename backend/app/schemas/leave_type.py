from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class LeaveTypeCreate(BaseModel):
    name: str
    description: str | None = None
    is_paid: bool = True

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Leave type name must not be empty")
        return v.strip()


class LeaveTypeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_paid: bool | None = None
    is_active: bool | None = None


class LeaveTypeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    is_paid: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
