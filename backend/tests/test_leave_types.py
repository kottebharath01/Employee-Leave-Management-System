from app.core.enums import Role
from tests.conftest import make_employee, login_headers


def test_hr_can_create_leave_type(client, db_session):
    hr = make_employee(db_session, "HR Person", "hrlt1@company.com", Role.HR_ASSOCIATE)
    headers = login_headers(client, "hrlt1@company.com")
    resp = client.post("/api/leave-types", json={"name": "Maternity Leave", "is_paid": True}, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["name"] == "Maternity Leave"


def test_duplicate_leave_type_rejected(client, db_session):
    hr = make_employee(db_session, "HR Person", "hrlt2@company.com", Role.HR_ASSOCIATE)
    headers = login_headers(client, "hrlt2@company.com")
    client.post("/api/leave-types", json={"name": "Bereavement Leave", "is_paid": True}, headers=headers)
    resp = client.post("/api/leave-types", json={"name": "Bereavement Leave", "is_paid": True}, headers=headers)
    assert resp.status_code == 409


def test_invalid_leave_type_data_rejected(client, db_session):
    hr = make_employee(db_session, "HR Person", "hrlt3@company.com", Role.HR_ASSOCIATE)
    headers = login_headers(client, "hrlt3@company.com")
    resp = client.post("/api/leave-types", json={"name": "   ", "is_paid": True}, headers=headers)
    assert resp.status_code == 422


def test_unauthorized_leave_type_creation(client, db_session):
    make_employee(db_session, "Plain Employee", "plain2@company.com", Role.EMPLOYEE)
    headers = login_headers(client, "plain2@company.com")
    resp = client.post("/api/leave-types", json={"name": "Some Leave", "is_paid": True}, headers=headers)
    assert resp.status_code == 403


def test_any_authenticated_user_can_list_leave_types(client, db_session):
    make_employee(db_session, "Plain Employee", "plain3@company.com", Role.EMPLOYEE)
    headers = login_headers(client, "plain3@company.com")
    resp = client.get("/api/leave-types", headers=headers)
    assert resp.status_code == 200
