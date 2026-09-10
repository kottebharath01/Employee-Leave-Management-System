from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.employee import Employee
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.employee import EmployeeOut
from app.services.auth_service import login

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login_route(payload: LoginRequest, db: Session = Depends(get_db)):
    token = login(db, payload.email, payload.password)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=EmployeeOut)
def get_me(current_user: Employee = Depends(get_current_user)):
    return current_user
