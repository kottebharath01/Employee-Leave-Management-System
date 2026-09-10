"""
Shared pytest fixtures.

Uses a SEPARATE PostgreSQL database (leave_management_test) so tests never
touch development data. Each test runs inside a transaction that is rolled
back afterwards, so tests are fully isolated from one another.
"""
import os
from urllib.parse import urlparse, urlunparse
from dotenv import load_dotenv

load_dotenv()

test_db_url = os.environ.get("TEST_DATABASE_URL")
if not test_db_url:
    base_url = os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres@localhost:5432/employee_leave_db",
    )
    parsed = urlparse(base_url)
    test_db_url = urlunparse(parsed._replace(path="/leave_management_test"))

os.environ["DATABASE_URL"] = test_db_url
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-not-for-production")

import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.enums import Role
from app.core.security import hash_password
from app.database.session import Base, get_db
from app.main import app
from app.models.department import Department
from app.models.employee import Employee
from app.models.holiday import Holiday
from app.models.leave_balance import LeaveBalance
from app.models.leave_type import LeaveType

engine = create_engine(settings.DATABASE_URL, future=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create all tables once for the whole test session, drop afterwards."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    """
    Provide a SQLAlchemy session bound to a transaction that is rolled back
    after each test, keeping tests isolated without recreating tables.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    """FastAPI TestClient wired to use the same transactional test session."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Helper factories used across many test modules
# ---------------------------------------------------------------------------


def make_employee(
    db_session,
    name,
    email,
    role,
    manager=None,
    is_active=True,
    is_admin=False,
    department=None,
    password="Password123",
):
    emp = Employee(
        name=name,
        email=email.lower(),
        password_hash=hash_password(password),
        role=role,
        department_id=department.id if department else None,
        manager_id=manager.id if manager else None,
        is_active=is_active,
        is_admin=is_admin,
    )
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)
    return emp


def make_department(db_session, name="Engineering"):
    dept = Department(name=name)
    db_session.add(dept)
    db_session.commit()
    db_session.refresh(dept)
    return dept


def make_leave_type(db_session, name="Paid Leave", is_paid=True, is_active=True):
    lt = LeaveType(name=name, is_paid=is_paid, is_active=is_active)
    db_session.add(lt)
    db_session.commit()
    db_session.refresh(lt)
    return lt


def make_holiday(db_session, holiday_date, name="Holiday", is_active=True):
    h = Holiday(holiday_date=holiday_date, name=name, is_active=is_active)
    db_session.add(h)
    db_session.commit()
    db_session.refresh(h)
    return h


def set_balance(db_session, employee, leave_type, year, total_days):
    balance = LeaveBalance(
        employee_id=employee.id, leave_type_id=leave_type.id, year=year, total_days=total_days, used_days=0
    )
    db_session.add(balance)
    db_session.commit()
    db_session.refresh(balance)
    return balance


def login_headers(client, email, password="Password123"):
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def next_monday(weeks_ahead=1) -> date:
    """Return a date that is guaranteed to be a Monday, N weeks from today."""
    today = date.today()
    days_ahead = (7 - today.weekday()) % 7 or 7
    monday = today + timedelta(days=days_ahead + (weeks_ahead - 1) * 7)
    return monday
