from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import require_approver, get_current_user
from app.models.employee import Employee
from app.schemas.leave_request import LeaveRequestOut, ApprovalActionIn
from app.schemas.misc import ApprovalHistoryOut
from app.services import leave_request_service
from app.utils.exceptions import AuthorizationError

router = APIRouter(prefix="/api/approvals", tags=["Approvals"])


@router.get("/pending", response_model=list[LeaveRequestOut])
def list_pending_approvals_route(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_approver),
):
    return leave_request_service.list_pending_for_approver(db, current_user.id)


@router.post("/{leave_request_id}/approve", response_model=LeaveRequestOut)
def approve_route(
    leave_request_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_approver),
):
    return leave_request_service.approve_leave_request(db, current_user, leave_request_id)


@router.post("/{leave_request_id}/reject", response_model=LeaveRequestOut)
def reject_route(
    leave_request_id: int,
    payload: ApprovalActionIn,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_approver),
):
    return leave_request_service.reject_leave_request(db, current_user, leave_request_id, payload.reason)


@router.get("/{leave_request_id}/history", response_model=list[ApprovalHistoryOut])
def get_approval_history_route(
    leave_request_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    from app.core.enums import HR_ROLES, APPROVER_ROLES

    leave_request = leave_request_service.get_leave_request(db, leave_request_id)
    is_owner = leave_request.employee_id == current_user.id
    is_hr_or_admin = current_user.role in HR_ROLES or current_user.is_admin
    is_approver_role = current_user.role in APPROVER_ROLES
    if not (is_owner or is_hr_or_admin or is_approver_role):
        raise AuthorizationError("You do not have permission to view this approval history.")
    return leave_request.approval_history
