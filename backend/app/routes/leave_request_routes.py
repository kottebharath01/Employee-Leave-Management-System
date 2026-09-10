from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.employee import Employee
from app.schemas.leave_request import (
    LeaveRequestCreate,
    LeaveRequestUpdate,
    LeaveRequestOut,
    LeaveRequestPreviewIn,
    LeaveRequestPreviewOut,
)
from app.services import leave_request_service
from app.utils.exceptions import AuthorizationError

router = APIRouter(prefix="/api/leave-requests", tags=["Leave Requests"])


@router.post("/preview", response_model=LeaveRequestPreviewOut)
def preview_leave_request_route(
    payload: LeaveRequestPreviewIn,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    return leave_request_service.preview_leave_request(db, current_user, payload)


@router.post("", response_model=LeaveRequestOut, status_code=201)
def create_leave_request_route(
    payload: LeaveRequestCreate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    return leave_request_service.create_leave_request(db, current_user, payload)


@router.get("/me", response_model=list[LeaveRequestOut])
def list_my_leave_requests_route(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    return leave_request_service.list_own_leave_requests(db, current_user.id)


@router.get("/{leave_request_id}", response_model=LeaveRequestOut)
def get_leave_request_route(
    leave_request_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    leave_request = leave_request_service.get_leave_request(db, leave_request_id)
    # Owner, the assigned approver, or HR/Admin may view it.
    from app.core.enums import HR_ROLES

    is_owner = leave_request.employee_id == current_user.id
    is_assigned_approver = leave_request.current_approver_id == current_user.id
    is_hr_or_admin = current_user.role in HR_ROLES or current_user.is_admin
    if not (is_owner or is_assigned_approver or is_hr_or_admin):
        raise AuthorizationError("You do not have permission to view this leave request.")
    return leave_request


@router.put("/{leave_request_id}", response_model=LeaveRequestOut)
def update_leave_request_route(
    leave_request_id: int,
    payload: LeaveRequestUpdate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    return leave_request_service.update_leave_request(db, current_user, leave_request_id, payload)


@router.post("/{leave_request_id}/cancel", response_model=LeaveRequestOut)
def cancel_leave_request_route(
    leave_request_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    return leave_request_service.cancel_leave_request(db, current_user, leave_request_id)
