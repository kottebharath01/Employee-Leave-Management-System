from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.enums import ALL_ROLES
from app.database.session import get_db
from app.dependencies.auth import require_admin
from app.models.employee import Employee
from app.schemas.employee import EmployeeOut
from app.services import employee_service

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/users", response_model=list[EmployeeOut])
def list_all_users_route(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_admin),
):
    """Admin-only: full list of all system users regardless of role."""
    return employee_service.list_employees(db)


@router.get("/roles")
def list_roles_route(current_user: Employee = Depends(require_admin)):
    """Admin-only: list all valid roles in the system."""
    return {"roles": sorted(ALL_ROLES)}


@router.patch("/users/{employee_id}/activate", response_model=EmployeeOut)
def admin_activate_user_route(
    employee_id: int, db: Session = Depends(get_db), current_user: Employee = Depends(require_admin)
):
    return employee_service.set_employee_active_status(db, employee_id, True)


@router.patch("/users/{employee_id}/deactivate", response_model=EmployeeOut)
def admin_deactivate_user_route(
    employee_id: int, db: Session = Depends(get_db), current_user: Employee = Depends(require_admin)
):
    return employee_service.set_employee_active_status(db, employee_id, False)
