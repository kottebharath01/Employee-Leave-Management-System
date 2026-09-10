from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user, require_hr
from app.models.employee import Employee
from app.schemas.leave_balance import LeaveBalanceSet, LeaveBalanceOut
from app.services import leave_balance_service
from app.utils.exceptions import AuthorizationError

router = APIRouter(prefix="/api/leave-balances", tags=["Leave Balances"])


def _to_out(balance) -> LeaveBalanceOut:
    return LeaveBalanceOut(
        id=balance.id,
        employee_id=balance.employee_id,
        leave_type_id=balance.leave_type_id,
        year=balance.year,
        total_days=float(balance.total_days),
        used_days=float(balance.used_days),
        available_days=balance.available_days,
        created_at=balance.created_at,
        updated_at=balance.updated_at,
    )


@router.get("/me", response_model=list[LeaveBalanceOut])
def get_my_balances(
    year: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    year = year or date.today().year
    balances = leave_balance_service.list_balances_for_employee(db, current_user.id, year)
    return [_to_out(b) for b in balances]


@router.get("/employee/{employee_id}", response_model=list[LeaveBalanceOut])
def get_employee_balances(
    employee_id: int,
    year: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    # Employees may only view their own balance; HR can view anyone's.
    from app.core.enums import HR_ROLES

    if employee_id != current_user.id and current_user.role not in HR_ROLES:
        raise AuthorizationError("You cannot view another employee's leave balance.")

    year = year or date.today().year
    balances = leave_balance_service.list_balances_for_employee(db, employee_id, year)
    return [_to_out(b) for b in balances]


@router.put("", response_model=LeaveBalanceOut)
def set_balance_route(
    payload: LeaveBalanceSet,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_hr),
):
    balance = leave_balance_service.set_balance(db, payload)
    return _to_out(balance)
