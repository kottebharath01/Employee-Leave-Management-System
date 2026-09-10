from app.core.enums import Role
from tests.conftest import make_employee, make_department, login_headers


def test_hr_can_create_employee(client, db_session):
    hr = make_employee(db_session, "HR Person", "hr1@company.com", Role.HR_ASSOCIATE)
    headers = login_headers(client, "hr1@company.com")
    resp = client.post(
        "/api/employees",
        json={"name": "New Guy", "email": "newguy@company.com", "password": "Password123", "role": "EMPLOYEE"},
        headers=headers,
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["email"] == "newguy@company.com"
    assert "password" not in body
    assert "password_hash" not in body
    assert body["is_active"] is True


def test_duplicate_email_rejected(client, db_session):
    hr = make_employee(db_session, "HR Person", "hr2@company.com", Role.HR_ASSOCIATE)
    make_employee(db_session, "Existing", "dup@company.com", Role.EMPLOYEE)
    headers = login_headers(client, "hr2@company.com")
    resp = client.post(
        "/api/employees",
        json={"name": "Dup", "email": "dup@company.com", "password": "Password123", "role": "EMPLOYEE"},
        headers=headers,
    )
    assert resp.status_code == 409


def test_invalid_manager_rejected(client, db_session):
    hr = make_employee(db_session, "HR Person", "hr3@company.com", Role.HR_ASSOCIATE)
    headers = login_headers(client, "hr3@company.com")
    resp = client.post(
        "/api/employees",
        json={
            "name": "Orphan",
            "email": "orphan@company.com",
            "password": "Password123",
            "role": "EMPLOYEE",
            "manager_id": 9999,
        },
        headers=headers,
    )
    assert resp.status_code == 404


def test_inactive_manager_rejected(client, db_session):
    hr = make_employee(db_session, "HR Person", "hr4@company.com", Role.HR_ASSOCIATE)
    inactive_manager = make_employee(db_session, "Inactive Mgr", "inactivemgr@company.com", Role.MANAGER, is_active=False)
    headers = login_headers(client, "hr4@company.com")
    resp = client.post(
        "/api/employees",
        json={
            "name": "Report",
            "email": "report@company.com",
            "password": "Password123",
            "role": "EMPLOYEE",
            "manager_id": inactive_manager.id,
        },
        headers=headers,
    )
    assert resp.status_code == 422


def test_invalid_role_rejected(client, db_session):
    hr = make_employee(db_session, "HR Person", "hr5@company.com", Role.HR_ASSOCIATE)
    headers = login_headers(client, "hr5@company.com")
    resp = client.post(
        "/api/employees",
        json={"name": "BadRole", "email": "badrole@company.com", "password": "Password123", "role": "SUPERHERO"},
        headers=headers,
    )
    assert resp.status_code == 422


def test_unauthorized_employee_creation(client, db_session):
    """A plain employee (not HR/Admin) cannot create employees."""
    make_employee(db_session, "Plain Employee", "plain1@company.com", Role.EMPLOYEE)
    headers = login_headers(client, "plain1@company.com")
    resp = client.post(
        "/api/employees",
        json={"name": "X", "email": "x@company.com", "password": "Password123", "role": "EMPLOYEE"},
        headers=headers,
    )
    assert resp.status_code == 403


def test_update_employee(client, db_session):
    hr = make_employee(db_session, "HR Person", "hr6@company.com", Role.HR_ASSOCIATE)
    target = make_employee(db_session, "Update Me", "updateme@company.com", Role.EMPLOYEE)
    headers = login_headers(client, "hr6@company.com")
    resp = client.put(f"/api/employees/{target.id}", json={"name": "Updated Name"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated Name"


def test_deactivate_employee(client, db_session):
    hr = make_employee(db_session, "HR Person", "hr7@company.com", Role.HR_ASSOCIATE)
    target = make_employee(db_session, "Deactivate Me", "deactivateme@company.com", Role.EMPLOYEE)
    headers = login_headers(client, "hr7@company.com")
    resp = client.patch(f"/api/employees/{target.id}/deactivate", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


def test_inactive_employee_cannot_login(client, db_session):
    hr = make_employee(db_session, "HR Person", "hr8@company.com", Role.HR_ASSOCIATE)
    target = make_employee(db_session, "ToDeactivate", "todeactivate@company.com", Role.EMPLOYEE)
    headers = login_headers(client, "hr8@company.com")
    client.patch(f"/api/employees/{target.id}/deactivate", headers=headers)

    login_resp = client.post(
        "/api/auth/login", json={"email": "todeactivate@company.com", "password": "Password123"}
    )
    assert login_resp.status_code == 401


def test_employee_cannot_view_others_profile(client, db_session):
    make_employee(db_session, "Viewer", "viewer@company.com", Role.EMPLOYEE)
    other = make_employee(db_session, "Other Person", "other1@company.com", Role.EMPLOYEE)
    headers = login_headers(client, "viewer@company.com")
    resp = client.get(f"/api/employees/{other.id}", headers=headers)
    assert resp.status_code == 403


def test_employee_can_view_own_profile(client, db_session):
    emp = make_employee(db_session, "Self Viewer", "selfviewer@company.com", Role.EMPLOYEE)
    headers = login_headers(client, "selfviewer@company.com")
    resp = client.get(f"/api/employees/{emp.id}", headers=headers)
    assert resp.status_code == 200
