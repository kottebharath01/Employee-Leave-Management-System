from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.department import Department
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.utils.exceptions import ConflictError, NotFoundError, ValidationAppError


def create_employee(db: Session, data: EmployeeCreate) -> Employee:
    email = data.email.lower()

    existing = db.query(Employee).filter(Employee.email == email).first()
    if existing:
        raise ConflictError(f"An employee with email '{email}' already exists.")

    if data.department_id is not None:
        department = db.query(Department).filter(Department.id == data.department_id).first()
        if not department:
            raise NotFoundError(f"Department with id {data.department_id} does not exist.")

    if data.manager_id is not None:
        manager = db.query(Employee).filter(Employee.id == data.manager_id).first()
        if not manager:
            raise NotFoundError(f"Manager with id {data.manager_id} does not exist.")
        if not manager.is_active:
            raise ValidationAppError("Assigned manager must be an active employee.")

    employee = Employee(
        name=data.name,
        email=email,
        password_hash=hash_password(data.password),
        role=data.role,
        department_id=data.department_id,
        manager_id=data.manager_id,
        is_admin=data.is_admin,
        is_active=True,
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def get_employee(db: Session, employee_id: int) -> Employee:
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise NotFoundError(f"Employee with id {employee_id} not found.")
    return employee


def list_employees(db: Session, department_id: int | None = None, is_active: bool | None = None) -> list[Employee]:
    query = db.query(Employee)
    if department_id is not None:
        query = query.filter(Employee.department_id == department_id)
    if is_active is not None:
        query = query.filter(Employee.is_active == is_active)
    return query.order_by(Employee.id).all()


def update_employee(db: Session, employee_id: int, data: EmployeeUpdate) -> Employee:
    employee = get_employee(db, employee_id)

    if data.manager_id is not None:
        if data.manager_id == employee_id:
            raise ValidationAppError("An employee cannot be their own manager.")
        manager = db.query(Employee).filter(Employee.id == data.manager_id).first()
        if not manager:
            raise NotFoundError(f"Manager with id {data.manager_id} does not exist.")
        if not manager.is_active:
            raise ValidationAppError("Assigned manager must be an active employee.")
        employee.manager_id = data.manager_id

    if data.department_id is not None:
        department = db.query(Department).filter(Department.id == data.department_id).first()
        if not department:
            raise NotFoundError(f"Department with id {data.department_id} does not exist.")
        employee.department_id = data.department_id

    if data.name is not None:
        employee.name = data.name
    if data.role is not None:
        employee.role = data.role
    if data.is_admin is not None:
        employee.is_admin = data.is_admin

    db.commit()
    db.refresh(employee)
    return employee


def set_employee_active_status(db: Session, employee_id: int, is_active: bool) -> Employee:
    employee = get_employee(db, employee_id)
    employee.is_active = is_active
    db.commit()
    db.refresh(employee)
    return employee
