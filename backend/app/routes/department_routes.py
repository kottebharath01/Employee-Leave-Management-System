from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user, require_hr
from app.models.department import Department
from app.models.employee import Employee
from app.schemas.misc import DepartmentCreate, DepartmentOut
from app.utils.exceptions import ConflictError

router = APIRouter(prefix="/api/departments", tags=["Departments"])


@router.post("", response_model=DepartmentOut, status_code=201)
def create_department_route(
    payload: DepartmentCreate, db: Session = Depends(get_db), current_user: Employee = Depends(require_hr)
):
    existing = db.query(Department).filter(Department.name.ilike(payload.name)).first()
    if existing:
        raise ConflictError(f"A department named '{payload.name}' already exists.")
    department = Department(name=payload.name, description=payload.description)
    db.add(department)
    db.commit()
    db.refresh(department)
    return department


@router.get("", response_model=list[DepartmentOut])
def list_departments_route(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    return db.query(Department).order_by(Department.id).all()
