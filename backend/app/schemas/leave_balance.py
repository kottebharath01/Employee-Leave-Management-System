from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class LeaveBalanceSet(BaseModel):
    employee_id: int
    leave_type_id: int
    year: int
    total_days: float

    @field_validator("total_days")
    @classmethod
    def validate_total_days(cls, v: float) -> float:
        if v < 0:
            raise ValueError("total_days cannot be negative")
        return v


class LeaveBalanceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    leave_type_id: int
    year: int
    total_days: float
    used_days: float
    available_days: float
    created_at: datetime
    updated_at: datetime
