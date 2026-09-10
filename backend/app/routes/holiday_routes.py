from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user, require_hr
from app.models.employee import Employee
from app.schemas.misc import HolidayCreate, HolidayUpdate, HolidayOut
from app.services import holiday_service

router = APIRouter(prefix="/api/holidays", tags=["Holidays"])


@router.post("", response_model=HolidayOut, status_code=201)
def create_holiday_route(
    payload: HolidayCreate, db: Session = Depends(get_db), current_user: Employee = Depends(require_hr)
):
    return holiday_service.create_holiday(db, payload)


@router.get("", response_model=list[HolidayOut])
def list_holidays_route(
    is_active: bool | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    return holiday_service.list_holidays(db, is_active=is_active)


@router.put("/{holiday_id}", response_model=HolidayOut)
def update_holiday_route(
    holiday_id: int,
    payload: HolidayUpdate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_hr),
):
    return holiday_service.update_holiday(db, holiday_id, payload)


@router.delete("/{holiday_id}", status_code=204)
def delete_holiday_route(
    holiday_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_hr),
):
    holiday_service.delete_holiday(db, holiday_id)
    return None
