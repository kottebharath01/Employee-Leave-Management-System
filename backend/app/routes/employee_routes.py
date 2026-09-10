from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.enums import HR_ROLES
from app.database.session import get_db
from app.dependencies.auth import get_current_user, require_hr, require_admin
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeOut
from app.services import employee_service
from app.utils.exceptions import AuthorizationError

router = APIRouter(prefix="/api/employees", tags=["Employees"])


def _require_hr_or_admin(current_user: Employee) -> None:
    if current_user.role not in HR_ROLES and not current_user.is_admin:
        raise AuthorizationError("HR or Admin access required.")


@router.post("", response_model=EmployeeOut, status_code=201)
def create_employee_route(
    payload: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    _require_hr_or_admin(current_user)
    return employee_service.create_employee(db, payload)


@router.get("", response_model=list[EmployeeOut])
def list_employees_route(
    department_id: int | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    _require_hr_or_admin(current_user)
    return employee_service.list_employees(db, department_id=department_id, is_active=is_active)


@router.get("/{employee_id}", response_model=EmployeeOut)
def get_employee_route(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    # Employees may view their own profile; HR/Admin may view anyone's.
    if employee_id != current_user.id:
        _require_hr_or_admin(current_user)
    return employee_service.get_employee(db, employee_id)


@router.put("/{employee_id}", response_model=EmployeeOut)
def update_employee_route(
    employee_id: int,
    payload: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    _require_hr_or_admin(current_user)
    return employee_service.update_employee(db, employee_id, payload)


@router.patch("/{employee_id}/activate", response_model=EmployeeOut)
def activate_employee_route(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    _require_hr_or_admin(current_user)
    return employee_service.set_employee_active_status(db, employee_id, True)


@router.patch("/{employee_id}/deactivate", response_model=EmployeeOut)
def deactivate_employee_route(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    _require_hr_or_admin(current_user)
    return employee_service.set_employee_active_status(db, employee_id, False)
