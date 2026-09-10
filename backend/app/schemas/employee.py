from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict, field_validator

from app.core.enums import Role, ALL_ROLES


class EmployeeCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str
    department_id: int | None = None
    manager_id: int | None = None
    is_admin: bool = False

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in ALL_ROLES:
            raise ValueError(f"Invalid role '{v}'. Must be one of: {sorted(ALL_ROLES)}")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Name must not be empty")
        return v.strip()


class EmployeeUpdate(BaseModel):
    name: str | None = None
    department_id: int | None = None
    manager_id: int | None = None
    role: str | None = None
    is_admin: bool | None = None

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str | None) -> str | None:
        if v is not None and v not in ALL_ROLES:
            raise ValueError(f"Invalid role '{v}'. Must be one of: {sorted(ALL_ROLES)}")
        return v


class EmployeeOut(BaseModel):
    """Note: password / password_hash are intentionally NEVER included."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: str
    department_id: int | None
    manager_id: int | None
    is_admin: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
