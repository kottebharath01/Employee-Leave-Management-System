from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.enums import Role, HR_ROLES, APPROVER_ROLES
from app.core.security import decode_access_token
from app.database.session import get_db
from app.models.employee import Employee

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Employee:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        raise credentials_exception

    try:
        payload = decode_access_token(token)
        employee_id_str = payload.get("sub")
        if employee_id_str is None:
            raise credentials_exception
        employee_id = int(employee_id_str)
    except (JWTError, ValueError, TypeError):
        raise credentials_exception

    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if employee is None:
        raise credentials_exception
    if not employee.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This account has been deactivated.",
        )
    return employee


def require_roles(*allowed_roles: str):
    """Dependency factory: require the current user to have one of the given roles."""

    def dependency(current_user: Employee = Depends(get_current_user)) -> Employee:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
        return current_user

    return dependency


def require_hr(current_user: Employee = Depends(get_current_user)) -> Employee:
    if current_user.role not in HR_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="HR access required.")
    return current_user


def require_admin(current_user: Employee = Depends(get_current_user)) -> Employee:
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required.")
    return current_user


def require_approver(current_user: Employee = Depends(get_current_user)) -> Employee:
    if current_user.role not in APPROVER_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Approver access required.")
    return current_user
