from app.core.enums import Role
from tests.conftest import make_employee, make_leave_type, set_balance, login_headers


def test_correct_balance_returned(client, db_session):
    emp = make_employee(db_session, "Balance Owner", "balowner@company.com", Role.EMPLOYEE)
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, emp, lt, 2026, 12)
    headers = login_headers(client, "balowner@company.com")
    resp = client.get("/api/leave-balances/me?year=2026", headers=headers)
    assert resp.status_code == 200
    balances = resp.json()
    assert len(balances) == 1
    assert balances[0]["total_days"] == 12
    assert balances[0]["available_days"] == 12


def test_unauthorized_balance_access(client, db_session):
    make_employee(db_session, "Viewer", "balviewer@company.com", Role.EMPLOYEE)
    other = make_employee(db_session, "Other", "balother@company.com", Role.EMPLOYEE)
    headers = login_headers(client, "balviewer@company.com")
    resp = client.get(f"/api/leave-balances/employee/{other.id}", headers=headers)
    assert resp.status_code == 403


def test_hr_can_view_any_employee_balance(client, db_session):
    hr = make_employee(db_session, "HR Person", "hrbal1@company.com", Role.HR_ASSOCIATE)
    target = make_employee(db_session, "Target", "baltarget@company.com", Role.EMPLOYEE)
    headers = login_headers(client, "hrbal1@company.com")
    resp = client.get(f"/api/leave-balances/employee/{target.id}", headers=headers)
    assert resp.status_code == 200


def test_hr_can_set_balance(client, db_session):
    hr = make_employee(db_session, "HR Person", "hrbal2@company.com", Role.HR_ASSOCIATE)
    target = make_employee(db_session, "SetBalTarget", "setbaltarget@company.com", Role.EMPLOYEE)
    lt = make_leave_type(db_session, "Casual Leave")
    headers = login_headers(client, "hrbal2@company.com")
    resp = client.put(
        "/api/leave-balances",
        json={"employee_id": target.id, "leave_type_id": lt.id, "year": 2026, "total_days": 8},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["total_days"] == 8


def test_employee_cannot_set_balance(client, db_session):
    emp = make_employee(db_session, "NoAccess", "noaccessbal@company.com", Role.EMPLOYEE)
    lt = make_leave_type(db_session, "Sick Leave")
    headers = login_headers(client, "noaccessbal@company.com")
    resp = client.put(
        "/api/leave-balances",
        json={"employee_id": emp.id, "leave_type_id": lt.id, "year": 2026, "total_days": 5},
        headers=headers,
    )
    assert resp.status_code == 403
