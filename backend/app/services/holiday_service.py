from sqlalchemy.orm import Session

from app.models.holiday import Holiday
from app.schemas.misc import HolidayCreate, HolidayUpdate
from app.utils.exceptions import ConflictError, NotFoundError


def create_holiday(db: Session, data: HolidayCreate) -> Holiday:
    existing = db.query(Holiday).filter(Holiday.holiday_date == data.holiday_date).first()
    if existing:
        raise ConflictError(f"A holiday already exists on {data.holiday_date}.")

    holiday = Holiday(
        holiday_date=data.holiday_date,
        name=data.name,
        description=data.description,
        is_active=True,
    )
    db.add(holiday)
    db.commit()
    db.refresh(holiday)
    return holiday


def get_holiday(db: Session, holiday_id: int) -> Holiday:
    holiday = db.query(Holiday).filter(Holiday.id == holiday_id).first()
    if not holiday:
        raise NotFoundError(f"Holiday with id {holiday_id} not found.")
    return holiday


def list_holidays(db: Session, is_active: bool | None = None) -> list[Holiday]:
    query = db.query(Holiday)
    if is_active is not None:
        query = query.filter(Holiday.is_active == is_active)
    return query.order_by(Holiday.holiday_date).all()


def update_holiday(db: Session, holiday_id: int, data: HolidayUpdate) -> Holiday:
    holiday = get_holiday(db, holiday_id)

    if data.holiday_date is not None and data.holiday_date != holiday.holiday_date:
        existing = db.query(Holiday).filter(Holiday.holiday_date == data.holiday_date).first()
        if existing:
            raise ConflictError(f"A holiday already exists on {data.holiday_date}.")
        holiday.holiday_date = data.holiday_date

    if data.name is not None:
        holiday.name = data.name
    if data.description is not None:
        holiday.description = data.description
    if data.is_active is not None:
        holiday.is_active = data.is_active

    db.commit()
    db.refresh(holiday)
    return holiday


def delete_holiday(db: Session, holiday_id: int) -> None:
    holiday = get_holiday(db, holiday_id)
    db.delete(holiday)
    db.commit()
