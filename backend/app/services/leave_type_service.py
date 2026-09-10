from sqlalchemy.orm import Session

from app.models.leave_type import LeaveType
from app.schemas.leave_type import LeaveTypeCreate, LeaveTypeUpdate
from app.utils.exceptions import ConflictError, NotFoundError


def create_leave_type(db: Session, data: LeaveTypeCreate) -> LeaveType:
    existing = db.query(LeaveType).filter(LeaveType.name.ilike(data.name)).first()
    if existing:
        raise ConflictError(f"A leave type named '{data.name}' already exists.")

    leave_type = LeaveType(name=data.name, description=data.description, is_paid=data.is_paid, is_active=True)
    db.add(leave_type)
    db.commit()
    db.refresh(leave_type)
    return leave_type


def get_leave_type(db: Session, leave_type_id: int) -> LeaveType:
    leave_type = db.query(LeaveType).filter(LeaveType.id == leave_type_id).first()
    if not leave_type:
        raise NotFoundError(f"Leave type with id {leave_type_id} not found.")
    return leave_type


def list_leave_types(db: Session, is_active: bool | None = None) -> list[LeaveType]:
    query = db.query(LeaveType)
    if is_active is not None:
        query = query.filter(LeaveType.is_active == is_active)
    return query.order_by(LeaveType.id).all()


def update_leave_type(db: Session, leave_type_id: int, data: LeaveTypeUpdate) -> LeaveType:
    leave_type = get_leave_type(db, leave_type_id)

    if data.name is not None and data.name.lower() != leave_type.name.lower():
        existing = db.query(LeaveType).filter(LeaveType.name.ilike(data.name)).first()
        if existing:
            raise ConflictError(f"A leave type named '{data.name}' already exists.")
        leave_type.name = data.name

    if data.description is not None:
        leave_type.description = data.description
    if data.is_paid is not None:
        leave_type.is_paid = data.is_paid
    if data.is_active is not None:
        leave_type.is_active = data.is_active

    db.commit()
    db.refresh(leave_type)
    return leave_type
