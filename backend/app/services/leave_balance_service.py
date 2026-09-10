from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.leave_balance import LeaveBalance
from app.models.leave_type import LeaveType
from app.schemas.leave_balance import LeaveBalanceSet
from app.utils.exceptions import NotFoundError


def get_or_create_balance(db: Session, employee_id: int, leave_type_id: int, year: int) -> LeaveBalance:
    balance = (
        db.query(LeaveBalance)
        .filter(
            LeaveBalance.employee_id == employee_id,
            LeaveBalance.leave_type_id == leave_type_id,
            LeaveBalance.year == year,
        )
        .first()
    )
    if not balance:
        balance = LeaveBalance(employee_id=employee_id, leave_type_id=leave_type_id, year=year, total_days=0, used_days=0)
        db.add(balance)
        db.commit()
        db.refresh(balance)
    return balance


def list_balances_for_employee(db: Session, employee_id: int, year: int | None = None) -> list[LeaveBalance]:
    query = db.query(LeaveBalance).filter(LeaveBalance.employee_id == employee_id)
    if year is not None:
        query = query.filter(LeaveBalance.year == year)
    return query.order_by(LeaveBalance.leave_type_id).all()


def set_balance(db: Session, data: LeaveBalanceSet) -> LeaveBalance:
    employee = db.query(Employee).filter(Employee.id == data.employee_id).first()
    if not employee:
        raise NotFoundError(f"Employee with id {data.employee_id} not found.")

    leave_type = db.query(LeaveType).filter(LeaveType.id == data.leave_type_id).first()
    if not leave_type:
        raise NotFoundError(f"Leave type with id {data.leave_type_id} not found.")

    balance = get_or_create_balance(db, data.employee_id, data.leave_type_id, data.year)
    balance.total_days = data.total_days
    db.commit()
    db.refresh(balance)
    return balance


def deduct_balance(db: Session, employee_id: int, leave_type_id: int, year: int, days: float) -> LeaveBalance:
    """Deduct `days` paid days from the employee's balance for that year."""
    balance = get_or_create_balance(db, employee_id, leave_type_id, year)
    balance.used_days = float(balance.used_days) + days
    db.commit()
    db.refresh(balance)
    return balance


def restore_balance(db: Session, employee_id: int, leave_type_id: int, year: int, days: float) -> LeaveBalance:
    """Restore (add back) `days` paid days to the employee's balance for that year."""
    balance = get_or_create_balance(db, employee_id, leave_type_id, year)
    balance.used_days = max(0.0, float(balance.used_days) - days)
    db.commit()
    db.refresh(balance)
    return balance
