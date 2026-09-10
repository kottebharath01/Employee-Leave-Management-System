from datetime import timedelta

from app.core.enums import Role
from tests.conftest import make_employee, make_leave_type, make_holiday, set_balance, login_headers, next_monday


def _dates_for_days(n_days, start=None):
    """Return (start, end) covering n_days consecutive calendar days starting at `start` (default: next Monday)."""
    start = start or next_monday()
    end = start + timedelta(days=n_days - 1)
    return start, end


def test_one_day_leave(client, db_session):
    tl = make_employee(db_session, "TL OneDay", "tloneday@company.com", Role.TEAM_LEAD)
    emp = make_employee(db_session, "OneDay", "oneday@company.com", Role.EMPLOYEE, tl)
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, emp, lt, next_monday().year, 10)
    headers = login_headers(client, "oneday@company.com")
    monday = next_monday()
    resp = client.post(
        "/api/leave-requests",
        json={
            "leave_type_id": lt.id,
            "start_date": str(monday),
            "end_date": str(monday),
            "explanation": "Personal errand",
        },
        headers=headers,
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["paid_days"] == 1
    assert body["unpaid_days"] == 0
    assert body["status"] == "PENDING"


def test_multi_day_leave(client, db_session):
    tl = make_employee(db_session, "TL MultiDay", "tlmultiday@company.com", Role.TEAM_LEAD)
    emp = make_employee(db_session, "MultiDay", "multiday@company.com", Role.EMPLOYEE, tl)
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, emp, lt, next_monday().year, 10)
    headers = login_headers(client, "multiday@company.com")
    start, end = _dates_for_days(3)  # Mon-Wed
    resp = client.post(
        "/api/leave-requests",
        json={"leave_type_id": lt.id, "start_date": str(start), "end_date": str(end), "explanation": "Trip"},
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["paid_days"] == 3


def test_weekend_only_zero_working_days(client, db_session):
    emp = make_employee(db_session, "WeekendOnly", "weekendonly@company.com", Role.EMPLOYEE)
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, emp, lt, 2026, 10)
    headers = login_headers(client, "weekendonly@company.com")
    monday = next_monday()
    saturday = monday - timedelta(days=2)
    sunday = monday - timedelta(days=1)
    resp = client.post(
        "/api/leave-requests",
        json={
            "leave_type_id": lt.id,
            "start_date": str(saturday),
            "end_date": str(sunday),
            "explanation": "Weekend",
        },
        headers=headers,
    )
    assert resp.status_code == 422
    assert "zero valid working days" in resp.json()["detail"]


def test_holiday_only_zero_working_days(client, db_session):
    emp = make_employee(db_session, "HolidayOnly", "holidayonly@company.com", Role.EMPLOYEE)
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, emp, lt, next_monday().year, 10)
    monday = next_monday()
    make_holiday(db_session, monday, "Test Holiday")
    headers = login_headers(client, "holidayonly@company.com")
    resp = client.post(
        "/api/leave-requests",
        json={
            "leave_type_id": lt.id,
            "start_date": str(monday),
            "end_date": str(monday),
            "explanation": "On holiday",
        },
        headers=headers,
    )
    assert resp.status_code == 422
    assert "zero valid working days" in resp.json()["detail"]


def test_weekend_plus_holiday_combo(client, db_session):
    emp = make_employee(db_session, "ComboEmp", "comboemp@company.com", Role.EMPLOYEE)
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, emp, lt, next_monday().year, 10)
    monday = next_monday()
    saturday = monday - timedelta(days=2)
    make_holiday(db_session, monday, "Combo Holiday")
    headers = login_headers(client, "comboemp@company.com")
    resp = client.post(
        "/api/leave-requests",
        json={
            "leave_type_id": lt.id,
            "start_date": str(saturday),
            "end_date": str(monday),
            "explanation": "Weekend + holiday",
        },
        headers=headers,
    )
    assert resp.status_code == 422


def test_zero_balance_full_unpaid_requires_confirmation(client, db_session):
    tl = make_employee(db_session, "TL ZeroBal", "tlzerobal@company.com", Role.TEAM_LEAD)
    emp = make_employee(db_session, "ZeroBal", "zerobal@company.com", Role.EMPLOYEE, tl)
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, emp, lt, next_monday().year, 0)
    headers = login_headers(client, "zerobal@company.com")
    monday = next_monday()

    preview = client.post(
        "/api/leave-requests/preview",
        json={"leave_type_id": lt.id, "start_date": str(monday), "end_date": str(monday)},
        headers=headers,
    )
    assert preview.status_code == 200
    assert preview.json()["requires_confirmation"] is True
    assert preview.json()["unpaid_days"] == 1

    # Without confirmation -> rejected
    resp = client.post(
        "/api/leave-requests",
        json={"leave_type_id": lt.id, "start_date": str(monday), "end_date": str(monday), "explanation": "No balance"},
        headers=headers,
    )
    assert resp.status_code == 422

    # With confirmation -> accepted, all unpaid
    resp2 = client.post(
        "/api/leave-requests",
        json={
            "leave_type_id": lt.id,
            "start_date": str(monday),
            "end_date": str(monday),
            "explanation": "No balance",
            "confirm_unpaid": True,
        },
        headers=headers,
    )
    assert resp2.status_code == 201
    assert resp2.json()["paid_days"] == 0
    assert resp2.json()["unpaid_days"] == 1


def test_partial_paid_partial_unpaid(client, db_session):
    """5 available paid days, 7 requested working days -> 5 paid + 2 unpaid."""
    emp = make_employee(db_session, "PartialPaid", "partialpaid@company.com", Role.EMPLOYEE)
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, emp, lt, next_monday().year, 5)
    headers = login_headers(client, "partialpaid@company.com")
    start, end = _dates_for_days(7)  # Mon-Sun = 5 working days (weekend excluded)... need 7 WORKING days
    # 7 working days needs 9 calendar days (skip 1 weekend): Mon-Fri (5) + next Mon-Wed (3) = 8, adjust:
    start = next_monday()
    end = start + timedelta(days=13)  # two full weeks -> 10 working days
    preview = client.post(
        "/api/leave-requests/preview",
        json={"leave_type_id": lt.id, "start_date": str(start), "end_date": str(end)},
        headers=headers,
    )
    assert preview.status_code == 200
    body = preview.json()
    assert body["working_days"] == 10
    assert body["paid_days"] == 5
    assert body["unpaid_days"] == 5
    assert body["requires_confirmation"] is True


def test_overlapping_leave_rejected(client, db_session):
    tl = make_employee(db_session, "TL Overlap", "tloverlap@company.com", Role.TEAM_LEAD)
    emp = make_employee(db_session, "Overlap", "overlap@company.com", Role.EMPLOYEE, tl)
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, emp, lt, next_monday().year, 20)
    headers = login_headers(client, "overlap@company.com")
    start, end = _dates_for_days(3)
    resp1 = client.post(
        "/api/leave-requests",
        json={"leave_type_id": lt.id, "start_date": str(start), "end_date": str(end), "explanation": "First"},
        headers=headers,
    )
    assert resp1.status_code == 201

    overlap_start = start + timedelta(days=1)
    overlap_end = end + timedelta(days=1)
    resp2 = client.post(
        "/api/leave-requests",
        json={
            "leave_type_id": lt.id,
            "start_date": str(overlap_start),
            "end_date": str(overlap_end),
            "explanation": "Overlapping",
        },
        headers=headers,
    )
    assert resp2.status_code == 409


def test_invalid_leave_type_on_request(client, db_session):
    emp = make_employee(db_session, "BadType", "badtype@company.com", Role.EMPLOYEE)
    headers = login_headers(client, "badtype@company.com")
    monday = next_monday()
    resp = client.post(
        "/api/leave-requests",
        json={"leave_type_id": 99999, "start_date": str(monday), "end_date": str(monday), "explanation": "X"},
        headers=headers,
    )
    assert resp.status_code == 404


def test_inactive_leave_type_on_request(client, db_session):
    emp = make_employee(db_session, "InactiveType", "inactivetype@company.com", Role.EMPLOYEE)
    lt = make_leave_type(db_session, "Retired Leave", is_active=False)
    headers = login_headers(client, "inactivetype@company.com")
    monday = next_monday()
    resp = client.post(
        "/api/leave-requests",
        json={"leave_type_id": lt.id, "start_date": str(monday), "end_date": str(monday), "explanation": "X"},
        headers=headers,
    )
    assert resp.status_code == 422


def test_edit_before_approval_allowed(client, db_session):
    tl = make_employee(db_session, "TL EditMe", "tleditme@company.com", Role.TEAM_LEAD)
    emp = make_employee(db_session, "EditMe", "editme@company.com", Role.EMPLOYEE, tl)
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, emp, lt, next_monday().year, 10)
    headers = login_headers(client, "editme@company.com")
    monday = next_monday()
    create_resp = client.post(
        "/api/leave-requests",
        json={"leave_type_id": lt.id, "start_date": str(monday), "end_date": str(monday), "explanation": "Orig"},
        headers=headers,
    )
    req_id = create_resp.json()["id"]
    new_date = monday + timedelta(days=1)
    edit_resp = client.put(
        f"/api/leave-requests/{req_id}",
        json={"start_date": str(new_date), "end_date": str(new_date)},
        headers=headers,
    )
    assert edit_resp.status_code == 200
    assert edit_resp.json()["start_date"] == str(new_date)


def test_edit_after_approval_disallowed(client, db_session):
    emp = make_employee(db_session, "NoEdit", "noedit@company.com", Role.EMPLOYEE)
    tl = make_employee(db_session, "TL NoEdit", "tlnoedit@company.com", Role.TEAM_LEAD)
    emp.manager_id = tl.id
    db_session.commit()
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, emp, lt, next_monday().year, 10)

    emp_headers = login_headers(client, "noedit@company.com")
    monday = next_monday()
    create_resp = client.post(
        "/api/leave-requests",
        json={"leave_type_id": lt.id, "start_date": str(monday), "end_date": str(monday), "explanation": "Orig"},
        headers=emp_headers,
    )
    req_id = create_resp.json()["id"]

    tl_headers = login_headers(client, "tlnoedit@company.com")
    approve_resp = client.post(f"/api/approvals/{req_id}/approve", headers=tl_headers)
    assert approve_resp.status_code == 200

    edit_resp = client.put(
        f"/api/leave-requests/{req_id}",
        json={"explanation": "Trying to edit after approval"},
        headers=emp_headers,
    )
    assert edit_resp.status_code == 422


def test_cancel_before_start_allowed(client, db_session):
    tl = make_employee(db_session, "TL CancelMe", "tlcancelme@company.com", Role.TEAM_LEAD)
    emp = make_employee(db_session, "CancelMe", "cancelme@company.com", Role.EMPLOYEE, tl)
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, emp, lt, next_monday().year, 10)
    headers = login_headers(client, "cancelme@company.com")
    monday = next_monday()
    create_resp = client.post(
        "/api/leave-requests",
        json={"leave_type_id": lt.id, "start_date": str(monday), "end_date": str(monday), "explanation": "X"},
        headers=headers,
    )
    req_id = create_resp.json()["id"]
    cancel_resp = client.post(f"/api/leave-requests/{req_id}/cancel", headers=headers)
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "CANCELLED"


def test_cancel_approved_before_start_restores_balance(client, db_session):
    emp = make_employee(db_session, "CancelApproved", "cancelapproved@company.com", Role.EMPLOYEE)
    tl = make_employee(db_session, "TL CancelApproved", "tlcancelapproved@company.com", Role.TEAM_LEAD)
    emp.manager_id = tl.id
    db_session.commit()
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, emp, lt, next_monday().year, 10)

    emp_headers = login_headers(client, "cancelapproved@company.com")
    monday = next_monday()
    create_resp = client.post(
        "/api/leave-requests",
        json={"leave_type_id": lt.id, "start_date": str(monday), "end_date": str(monday), "explanation": "X"},
        headers=emp_headers,
    )
    req_id = create_resp.json()["id"]

    tl_headers = login_headers(client, "tlcancelapproved@company.com")
    client.post(f"/api/approvals/{req_id}/approve", headers=tl_headers)

    balance_before = client.get(f"/api/leave-balances/me?year={monday.year}", headers=emp_headers).json()[0]
    assert balance_before["used_days"] == 1

    cancel_resp = client.post(f"/api/leave-requests/{req_id}/cancel", headers=emp_headers)
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "CANCELLED"

    balance_after = client.get(f"/api/leave-balances/me?year={monday.year}", headers=emp_headers).json()[0]
    assert balance_after["used_days"] == 0
    assert balance_after["available_days"] == 10


def test_cancel_after_start_disallowed(client, db_session):
    emp = make_employee(db_session, "PastCancel", "pastcancel@company.com", Role.EMPLOYEE)
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, emp, lt, 2020, 10)
    headers = login_headers(client, "pastcancel@company.com")

    # Directly insert a past leave request (bypassing overlap/date validation of the
    # create endpoint, which would reject past dates implicitly via workflow) to
    # simulate a request whose start date has already passed.
    from app.models.leave_request import LeaveRequest
    from app.core.enums import LeaveRequestStatus
    from datetime import date, timedelta as td

    past_start = date.today() - td(days=5)
    leave_request = LeaveRequest(
        employee_id=emp.id,
        leave_type_id=lt.id,
        start_date=past_start,
        end_date=past_start,
        explanation="Past leave",
        status=LeaveRequestStatus.APPROVED,
        paid_days=1,
        unpaid_days=0,
    )
    db_session.add(leave_request)
    db_session.commit()
    db_session.refresh(leave_request)

    resp = client.post(f"/api/leave-requests/{leave_request.id}/cancel", headers=headers)
    assert resp.status_code == 422
    assert "already started" in resp.json()["detail"]


def test_duplicate_request_rejected_as_overlap(client, db_session):
    tl = make_employee(db_session, "TL DupReq", "tldupreq@company.com", Role.TEAM_LEAD)
    emp = make_employee(db_session, "DupReq", "dupreq@company.com", Role.EMPLOYEE, tl)
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, emp, lt, next_monday().year, 10)
    headers = login_headers(client, "dupreq@company.com")
    monday = next_monday()
    payload = {"leave_type_id": lt.id, "start_date": str(monday), "end_date": str(monday), "explanation": "Dup"}
    resp1 = client.post("/api/leave-requests", json=payload, headers=headers)
    assert resp1.status_code == 201
    resp2 = client.post("/api/leave-requests", json=payload, headers=headers)
    assert resp2.status_code == 409


def test_employee_with_no_manager_cannot_apply(client, db_session):
    """An employee with no manager assigned cannot have their leave routed."""
    emp = make_employee(db_session, "NoManager", "nomanager@company.com", Role.EMPLOYEE)
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, emp, lt, next_monday().year, 10)
    headers = login_headers(client, "nomanager@company.com")
    monday = next_monday()
    resp = client.post(
        "/api/leave-requests",
        json={"leave_type_id": lt.id, "start_date": str(monday), "end_date": str(monday), "explanation": "X"},
        headers=headers,
    )
    assert resp.status_code == 422
    assert "no manager assigned" in resp.json()["detail"].lower()


def test_ceo_leave_auto_approved(client, db_session):
    ceo = make_employee(db_session, "CEO Applicant", "ceoapplicant@company.com", Role.CEO)
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, ceo, lt, next_monday().year, 10)
    headers = login_headers(client, "ceoapplicant@company.com")
    monday = next_monday()
    resp = client.post(
        "/api/leave-requests",
        json={"leave_type_id": lt.id, "start_date": str(monday), "end_date": str(monday), "explanation": "CEO trip"},
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "APPROVED"
    assert resp.json()["current_approver_id"] is None
