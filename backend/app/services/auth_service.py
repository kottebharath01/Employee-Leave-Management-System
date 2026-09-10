from sqlalchemy.orm import Session

from app.core.security import verify_password, create_access_token
from app.models.employee import Employee
from app.utils.exceptions import AuthenticationError


def authenticate_employee(db: Session, email: str, password: str) -> Employee:
    """
    Validate credentials and account status.
    Raises AuthenticationError with a generic message on any failure so we
    don't leak whether the email exists or the password was wrong.
    """
    employee = db.query(Employee).filter(Employee.email == email.lower()).first()
    if not employee:
        raise AuthenticationError("Invalid email or password")

    if not verify_password(password, employee.password_hash):
        raise AuthenticationError("Invalid email or password")

    if not employee.is_active:
        raise AuthenticationError("This account has been deactivated. Contact HR/Admin.")

    return employee


def login(db: Session, email: str, password: str) -> str:
    employee = authenticate_employee(db, email, password)
    token = create_access_token(subject=str(employee.id), extra_claims={"role": employee.role})
    return token
