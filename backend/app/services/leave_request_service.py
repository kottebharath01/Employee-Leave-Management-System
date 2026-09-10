from datetime import date

from sqlalchemy.orm import Session

from app.core.enums import Role, LeaveRequestStatus, ApprovalAction, NotificationType
from app.models.approval_history import ApprovalHistory
from app.models.employee import Employee
from app.models.holiday import Holiday
from app.models.leave_request import LeaveRequest
from app.models.leave_type import LeaveType
from app.schemas.leave_request import LeaveRequestCreate, LeaveRequestUpdate, LeaveRequestPreviewIn
from app.services import leave_balance_service, notification_service
from app.utils.date_utils import count_working_days
from app.utils.exceptions import (
    NotFoundError,
    ValidationAppError,
    ConflictError,
    AuthorizationError,
)

# Statuses that "occupy" dates and therefore must be checked for overlap.
ACTIVE_STATUSES = (LeaveRequestStatus.PENDING, LeaveRequestStatus.APPROVED)


def _get_active_holiday_dates(db: Session) -> set[date]:
    holidays = db.query(Holiday).filter(Holiday.is_active.is_(True)).all()
    return {h.holiday_date for h in holidays}


def _get_leave_type_or_error(db: Session, leave_type_id: int) -> LeaveType:
    leave_type = db.query(LeaveType).filter(LeaveType.id == leave_type_id).first()
    if not leave_type:
        raise NotFoundError(f"Leave type with id {leave_type_id} not found.")
    if not leave_type.is_active:
        raise ValidationAppError(f"Leave type '{leave_type.name}' is not active and cannot be used.")
    return leave_type


def _check_overlap(
    db: Session, employee_id: int, start_date: date, end_date: date, exclude_request_id: int | None = None
) -> None:
    query = db.query(LeaveRequest).filter(
        LeaveRequest.employee_id == employee_id,
        LeaveRequest.status.in_(ACTIVE_STATUSES),
        LeaveRequest.start_date <= end_date,
        LeaveRequest.end_date >= start_date,
    )
    if exclude_request_id is not None:
        query = query.filter(LeaveRequest.id != exclude_request_id)

    overlapping = query.first()
    if overlapping:
        raise ConflictError(
            "These dates overlap with an existing leave request "
            f"(request #{overlapping.id}, {overlapping.start_date} to {overlapping.end_date}, "
            f"status {overlapping.status}). Please choose different dates."
        )


def _current_year(d: date) -> int:
    return d.year


def preview_leave_request(db: Session, employee: Employee, data: LeaveRequestPreviewIn) -> dict:
    """Compute working days + paid/unpaid split WITHOUT creating a request."""
    leave_type = _get_leave_type_or_error(db, data.leave_type_id)

    holiday_dates = _get_active_holiday_dates(db)
    working_days = count_working_days(data.start_date, data.end_date, holiday_dates)

    if working_days == 0:
        raise ValidationAppError(
            "The selected dates contain zero valid working days (weekends/holidays only). "
            "Please choose different dates."
        )

    if not leave_type.is_paid:
        available_paid_days = 0.0
        paid_days = 0.0
        unpaid_days = float(working_days)
    else:
        year = _current_year(data.start_date)
        balance = leave_balance_service.get_or_create_balance(db, employee.id, leave_type.id, year)
        available_paid_days = balance.available_days
        paid_days = min(available_paid_days, float(working_days))
        paid_days = max(paid_days, 0.0)
        unpaid_days = float(working_days) - paid_days

    requires_confirmation = unpaid_days > 0
    if requires_confirmation:
        message = (
            f"You have {available_paid_days:.0f} paid day(s) available. "
            f"Of the {working_days} requested working day(s), {paid_days:.0f} will be paid and "
            f"{unpaid_days:.0f} will be unpaid. Do you want to continue?"
        )
    else:
        message = f"All {working_days} requested working day(s) will be paid leave."

    return {
        "working_days": working_days,
        "available_paid_days": available_paid_days,
        "paid_days": paid_days,
        "unpaid_days": unpaid_days,
        "requires_confirmation": requires_confirmation,
        "message": message,
    }


def _resolve_approver(db: Session, employee: Employee) -> Employee | None:
    """
    Determine who should approve this employee's leave request.

    The employee's manager (manager_id) is the assigned approver, matching
    the configured business/HR hierarchy. If the employee has no manager
    (e.g. the CEO), the request is auto-approved.
    """
    if employee.role == Role.CEO:
        return None

    if employee.manager_id is None:
        raise ValidationAppError(
            "This employee has no manager assigned, so their leave request cannot be routed "
            "for approval. Please contact HR/Admin to assign a manager."
        )

    manager = db.query(Employee).filter(Employee.id == employee.manager_id).first()
    if not manager:
        raise ValidationAppError("Assigned manager no longer exists. Please contact HR/Admin.")
    if not manager.is_active:
        raise ValidationAppError(
            "Assigned manager/approver is currently inactive. Please contact HR/Admin to reassign approval."
        )
    return manager


def create_leave_request(db: Session, employee: Employee, data: LeaveRequestCreate) -> LeaveRequest:
    leave_type = _get_leave_type_or_error(db, data.leave_type_id)

    _check_overlap(db, employee.id, data.start_date, data.end_date)

    holiday_dates = _get_active_holiday_dates(db)
    working_days = count_working_days(data.start_date, data.end_date, holiday_dates)
    if working_days == 0:
        raise ValidationAppError(
            "The selected dates contain zero valid working days (weekends/holidays only). "
            "Please choose different dates."
        )

    year = _current_year(data.start_date)

    if not leave_type.is_paid:
        paid_days = 0.0
        unpaid_days = float(working_days)
    else:
        balance = leave_balance_service.get_or_create_balance(db, employee.id, leave_type.id, year)
        available_paid_days = balance.available_days
        paid_days = max(min(available_paid_days, float(working_days)), 0.0)
        unpaid_days = float(working_days) - paid_days

    if unpaid_days > 0 and not data.confirm_unpaid:
        raise ValidationAppError(
            f"This request includes {unpaid_days:.0f} unpaid day(s) beyond your available paid balance. "
            "Resubmit with confirm_unpaid=true to proceed, or choose different dates."
        )

    approver = _resolve_approver(db, employee)

    leave_request = LeaveRequest(
        employee_id=employee.id,
        leave_type_id=leave_type.id,
        start_date=data.start_date,
        end_date=data.end_date,
        explanation=data.explanation,
        status=LeaveRequestStatus.PENDING,
        paid_days=paid_days,
        unpaid_days=unpaid_days,
        current_approver_id=approver.id if approver else None,
    )
    db.add(leave_request)
    db.commit()
    db.refresh(leave_request)

    if approver is None:
        # CEO: auto-approve immediately.
        _finalize_approval(db, leave_request, approver_id=None, auto=True)
    else:
        notification_service.create_notification(
            db,
            recipient_id=approver.id,
            notification_type=NotificationType.LEAVE_REQUEST_SUBMITTED,
            message=(
                f"{employee.name} submitted a leave request "
                f"({leave_request.start_date} to {leave_request.end_date}) awaiting your approval."
            ),
            leave_request_id=leave_request.id,
        )

    db.refresh(leave_request)
    return leave_request


def get_leave_request(db: Session, leave_request_id: int) -> LeaveRequest:
    leave_request = db.query(LeaveRequest).filter(LeaveRequest.id == leave_request_id).first()
    if not leave_request:
        raise NotFoundError(f"Leave request with id {leave_request_id} not found.")
    return leave_request


def list_own_leave_requests(db: Session, employee_id: int) -> list[LeaveRequest]:
    return (
        db.query(LeaveRequest)
        .filter(LeaveRequest.employee_id == employee_id)
        .order_by(LeaveRequest.created_at.desc())
        .all()
    )


def list_pending_for_approver(db: Session, approver_id: int) -> list[LeaveRequest]:
    return (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.current_approver_id == approver_id,
            LeaveRequest.status == LeaveRequestStatus.PENDING,
        )
        .order_by(LeaveRequest.created_at)
        .all()
    )


def update_leave_request(
    db: Session, employee: Employee, leave_request_id: int, data: LeaveRequestUpdate
) -> LeaveRequest:
    leave_request = get_leave_request(db, leave_request_id)

    if leave_request.employee_id != employee.id:
        raise AuthorizationError("You can only edit your own leave requests.")

    if leave_request.status != LeaveRequestStatus.PENDING:
        raise ValidationAppError(
            f"This leave request has status '{leave_request.status}' and can no longer be edited. "
            "Only PENDING requests can be edited."
        )

    new_leave_type_id = data.leave_type_id or leave_request.leave_type_id
    new_start = data.start_date or leave_request.start_date
    new_end = data.end_date or leave_request.end_date

    leave_type = _get_leave_type_or_error(db, new_leave_type_id)

    if new_end < new_start:
        raise ValidationAppError("end_date cannot be before start_date")

    _check_overlap(db, employee.id, new_start, new_end, exclude_request_id=leave_request.id)

    holiday_dates = _get_active_holiday_dates(db)
    working_days = count_working_days(new_start, new_end, holiday_dates)
    if working_days == 0:
        raise ValidationAppError(
            "The selected dates contain zero valid working days (weekends/holidays only). "
            "Please choose different dates."
        )

    year = _current_year(new_start)
    if not leave_type.is_paid:
        paid_days = 0.0
        unpaid_days = float(working_days)
    else:
        balance = leave_balance_service.get_or_create_balance(db, employee.id, leave_type.id, year)
        available_paid_days = balance.available_days
        paid_days = max(min(available_paid_days, float(working_days)), 0.0)
        unpaid_days = float(working_days) - paid_days

    if unpaid_days > 0 and not data.confirm_unpaid:
        raise ValidationAppError(
            f"This updated request includes {unpaid_days:.0f} unpaid day(s) beyond your available paid balance. "
            "Resubmit with confirm_unpaid=true to proceed, or choose different dates."
        )

    leave_request.leave_type_id = leave_type.id
    leave_request.start_date = new_start
    leave_request.end_date = new_end
    if data.explanation is not None:
        if not data.explanation.strip():
            raise ValidationAppError("explanation must not be empty")
        leave_request.explanation = data.explanation.strip()
    leave_request.paid_days = paid_days
    leave_request.unpaid_days = unpaid_days

    db.commit()
    db.refresh(leave_request)
    return leave_request


def cancel_leave_request(db: Session, employee: Employee, leave_request_id: int) -> LeaveRequest:
    leave_request = get_leave_request(db, leave_request_id)

    if leave_request.employee_id != employee.id:
        raise AuthorizationError("You can only cancel your own leave requests.")

    if leave_request.status not in (LeaveRequestStatus.PENDING, LeaveRequestStatus.APPROVED):
        raise ValidationAppError(f"This leave request has status '{leave_request.status}' and cannot be cancelled.")

    if leave_request.start_date <= date.today():
        raise ValidationAppError("This leave request has already started and cannot be cancelled.")

    was_approved = leave_request.status == LeaveRequestStatus.APPROVED

    leave_request.status = LeaveRequestStatus.CANCELLED
    db.add(
        ApprovalHistory(
            leave_request_id=leave_request.id,
            approver_id=employee.id,
            action=ApprovalAction.CANCELLED,
            reason="Cancelled by employee before start date.",
        )
    )

    if was_approved and float(leave_request.paid_days) > 0:
        year = _current_year(leave_request.start_date)
        leave_balance_service.restore_balance(
            db, employee.id, leave_request.leave_type_id, year, float(leave_request.paid_days)
        )

    db.commit()
    db.refresh(leave_request)
    return leave_request


def _finalize_approval(
    db: Session, leave_request: LeaveRequest, approver_id: int | None, auto: bool = False
) -> None:
    """Shared logic for approving a request (manual approve or CEO auto-approve)."""
    leave_request.status = LeaveRequestStatus.APPROVED
    leave_request.current_approver_id = None

    db.add(
        ApprovalHistory(
            leave_request_id=leave_request.id,
            approver_id=approver_id,
            action=ApprovalAction.AUTO_APPROVED if auto else ApprovalAction.APPROVED,
            reason=None,
        )
    )

    if float(leave_request.paid_days) > 0:
        year = _current_year(leave_request.start_date)
        leave_balance_service.deduct_balance(
            db, leave_request.employee_id, leave_request.leave_type_id, year, float(leave_request.paid_days)
        )

    notification_service.create_notification(
        db,
        recipient_id=leave_request.employee_id,
        notification_type=NotificationType.LEAVE_REQUEST_APPROVED,
        message=(
            f"Your leave request ({leave_request.start_date} to {leave_request.end_date}) has been approved."
        ),
        leave_request_id=leave_request.id,
    )
    db.commit()


def approve_leave_request(db: Session, approver: Employee, leave_request_id: int) -> LeaveRequest:
    leave_request = get_leave_request(db, leave_request_id)

    if leave_request.status != LeaveRequestStatus.PENDING:
        raise ValidationAppError(f"This leave request has status '{leave_request.status}' and cannot be approved.")

    if leave_request.current_approver_id != approver.id:
        raise AuthorizationError("You are not the assigned approver for this leave request.")

    _finalize_approval(db, leave_request, approver_id=approver.id, auto=False)
    db.refresh(leave_request)
    return leave_request


def reject_leave_request(db: Session, approver: Employee, leave_request_id: int, reason: str | None) -> LeaveRequest:
    leave_request = get_leave_request(db, leave_request_id)

    if leave_request.status != LeaveRequestStatus.PENDING:
        raise ValidationAppError(f"This leave request has status '{leave_request.status}' and cannot be rejected.")

    if leave_request.current_approver_id != approver.id:
        raise AuthorizationError("You are not the assigned approver for this leave request.")

    if not reason or not reason.strip():
        raise ValidationAppError("A rejection reason/explanation is required.")

    leave_request.status = LeaveRequestStatus.REJECTED
    leave_request.current_approver_id = None

    db.add(
        ApprovalHistory(
            leave_request_id=leave_request.id,
            approver_id=approver.id,
            action=ApprovalAction.REJECTED,
            reason=reason.strip(),
        )
    )

    notification_service.create_notification(
        db,
        recipient_id=leave_request.employee_id,
        notification_type=NotificationType.LEAVE_REQUEST_REJECTED,
        message=(
            f"Your leave request ({leave_request.start_date} to {leave_request.end_date}) was rejected: "
            f"{reason.strip()}"
        ),
        leave_request_id=leave_request.id,
    )

    db.commit()
    db.refresh(leave_request)
    return leave_request
