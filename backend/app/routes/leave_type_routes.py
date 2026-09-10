from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user, require_hr
from app.models.employee import Employee
from app.schemas.leave_type import LeaveTypeCreate, LeaveTypeUpdate, LeaveTypeOut
from app.services import leave_type_service

router = APIRouter(prefix="/api/leave-types", tags=["Leave Types"])


@router.post("", response_model=LeaveTypeOut, status_code=201)
def create_leave_type_route(
    payload: LeaveTypeCreate, db: Session = Depends(get_db), current_user: Employee = Depends(require_hr)
):
    return leave_type_service.create_leave_type(db, payload)


@router.get("", response_model=list[LeaveTypeOut])
def list_leave_types_route(
    is_active: bool | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    # Any authenticated user can view leave types (needed to apply for leave).
    return leave_type_service.list_leave_types(db, is_active=is_active)


@router.put("/{leave_type_id}", response_model=LeaveTypeOut)
def update_leave_type_route(
    leave_type_id: int,
    payload: LeaveTypeUpdate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_hr),
):
    return leave_type_service.update_leave_type(db, leave_type_id, payload)
