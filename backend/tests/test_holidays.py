from datetime import date

from app.core.enums import Role
from tests.conftest import make_employee, login_headers


def test_hr_can_create_holiday(client, db_session):
    hr = make_employee(db_session, "HR Person", "hrhol1@company.com", Role.HR_ASSOCIATE)
    headers = login_headers(client, "hrhol1@company.com")
    resp = client.post(
        "/api/holidays", json={"holiday_date": "2026-12-25", "name": "Christmas"}, headers=headers
    )
    assert resp.status_code == 201


def test_duplicate_holiday_date_rejected(client, db_session):
    hr = make_employee(db_session, "HR Person", "hrhol2@company.com", Role.HR_ASSOCIATE)
    headers = login_headers(client, "hrhol2@company.com")
    client.post("/api/holidays", json={"holiday_date": "2026-01-01", "name": "New Year"}, headers=headers)
    resp = client.post("/api/holidays", json={"holiday_date": "2026-01-01", "name": "Dup"}, headers=headers)
    assert resp.status_code == 409


def test_unauthorized_holiday_creation(client, db_session):
    make_employee(db_session, "Plain Employee", "plainhol@company.com", Role.EMPLOYEE)
    headers = login_headers(client, "plainhol@company.com")
    resp = client.post("/api/holidays", json={"holiday_date": "2026-07-04", "name": "X"}, headers=headers)
    assert resp.status_code == 403


def test_list_holidays_any_authenticated_user(client, db_session):
    make_employee(db_session, "Plain Employee", "plainhol2@company.com", Role.EMPLOYEE)
    headers = login_headers(client, "plainhol2@company.com")
    resp = client.get("/api/holidays", headers=headers)
    assert resp.status_code == 200


def test_hr_can_update_holiday(client, db_session):
    hr = make_employee(db_session, "HR Person", "hrhol3@company.com", Role.HR_ASSOCIATE)
    headers = login_headers(client, "hrhol3@company.com")
    create_resp = client.post(
        "/api/holidays", json={"holiday_date": "2026-05-01", "name": "Labor Day"}, headers=headers
    )
    holiday_id = create_resp.json()["id"]
    update_resp = client.put(f"/api/holidays/{holiday_id}", json={"is_active": False}, headers=headers)
    assert update_resp.status_code == 200
    assert update_resp.json()["is_active"] is False


def test_hr_can_delete_holiday(client, db_session):
    hr = make_employee(db_session, "HR Person", "hrhol4@company.com", Role.HR_ASSOCIATE)
    headers = login_headers(client, "hrhol4@company.com")
    create_resp = client.post(
        "/api/holidays", json={"holiday_date": "2026-08-15", "name": "Independence Day"}, headers=headers
    )
    holiday_id = create_resp.json()["id"]
    delete_resp = client.delete(f"/api/holidays/{holiday_id}", headers=headers)
    assert delete_resp.status_code == 204
