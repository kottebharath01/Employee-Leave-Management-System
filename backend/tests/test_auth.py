from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import settings
from tests.conftest import make_employee, login_headers
from app.core.enums import Role


def test_valid_login_returns_token(client, db_session):
    make_employee(db_session, "Test User", "valid@company.com", Role.EMPLOYEE)
    resp = client.post("/api/auth/login", json={"email": "valid@company.com", "password": "Password123"})
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_wrong_password(client, db_session):
    make_employee(db_session, "Test User", "wrongpass@company.com", Role.EMPLOYEE)
    resp = client.post("/api/auth/login", json={"email": "wrongpass@company.com", "password": "WrongPassword1"})
    assert resp.status_code == 401


def test_login_invalid_email(client, db_session):
    resp = client.post("/api/auth/login", json={"email": "doesnotexist@company.com", "password": "Password123"})
    assert resp.status_code == 401


def test_login_inactive_user(client, db_session):
    make_employee(db_session, "Inactive User", "inactive@company.com", Role.EMPLOYEE, is_active=False)
    resp = client.post("/api/auth/login", json={"email": "inactive@company.com", "password": "Password123"})
    assert resp.status_code == 401
    assert "deactivated" in resp.json()["detail"].lower()


def test_protected_route_missing_jwt(client, db_session):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_protected_route_invalid_jwt(client, db_session):
    resp = client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert resp.status_code == 401


def test_protected_route_expired_jwt(client, db_session):
    emp = make_employee(db_session, "Expired User", "expired@company.com", Role.EMPLOYEE)
    expired_payload = {
        "sub": str(emp.id),
        "role": emp.role,
        "iat": datetime.now(timezone.utc) - timedelta(hours=2),
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
    }
    expired_token = jwt.encode(expired_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert resp.status_code == 401


def test_protected_route_malformed_jwt(client, db_session):
    resp = client.get("/api/auth/me", headers={"Authorization": "Bearer abc.def"})
    assert resp.status_code == 401


def test_get_current_user_returns_no_password_fields(client, db_session):
    make_employee(db_session, "NoPwd User", "nopwd@company.com", Role.EMPLOYEE)
    headers = login_headers(client, "nopwd@company.com")
    resp = client.get("/api/auth/me", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "password" not in body
    assert "password_hash" not in body
