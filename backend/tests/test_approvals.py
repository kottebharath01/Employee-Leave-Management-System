from app.core.enums import Role
from tests.conftest import make_employee, make_leave_type, set_balance, login_headers, next_monday


def _apply_leave(client, emp_headers, lt_id):
    monday = next_monday()
    resp = client.post(
        "/api/leave-requests",
        json={"leave_type_id": lt_id, "start_date": str(monday), "end_date": str(monday), "explanation": "Testing"},
        headers=emp_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _build_chain(db_session, prefix):
    """Build a full Employee -> ... -> CEO chain for a test, all sharing the CEO node."""
    ceo = make_employee(db_session, f"{prefix} CEO", f"{prefix}ceo@company.com", Role.CEO)
    director = make_employee(db_session, f"{prefix} Director", f"{prefix}director@company.com", Role.DIRECTOR, ceo)
    sr_mgr = make_employee(db_session, f"{prefix} SrMgr", f"{prefix}srmgr@company.com", Role.SENIOR_MANAGER, director)
    mgr = make_employee(db_session, f"{prefix} Mgr", f"{prefix}mgr@company.com", Role.MANAGER, sr_mgr)
    tl = make_employee(db_session, f"{prefix} TL", f"{prefix}tl@company.com", Role.TEAM_LEAD, mgr)
    emp = make_employee(db_session, f"{prefix} Emp", f"{prefix}emp@company.com", Role.EMPLOYEE, tl)
    return {"ceo": ceo, "director": director, "sr_mgr": sr_mgr, "mgr": mgr, "tl": tl, "emp": emp}


def _build_hr_chain(db_session, prefix):
    ceo = make_employee(db_session, f"{prefix} CEO", f"{prefix}ceo@company.com", Role.CEO)
    hr_dir = make_employee(db_session, f"{prefix} HRDir", f"{prefix}hrdir@company.com", Role.HR_DIRECTOR, ceo)
    hr_mgr = make_employee(db_session, f"{prefix} HRMgr", f"{prefix}hrmgr@company.com", Role.HR_MANAGER, hr_dir)
    hr_assoc = make_employee(
        db_session, f"{prefix} HRAssoc", f"{prefix}hrassoc@company.com", Role.HR_ASSOCIATE, hr_mgr
    )
    return {"ceo": ceo, "hr_dir": hr_dir, "hr_mgr": hr_mgr, "hr_assoc": hr_assoc}


def test_employee_routes_to_team_lead(client, db_session):
    chain = _build_chain(db_session, "chain1")
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, chain["emp"], lt, next_monday().year, 10)
    emp_headers = login_headers(client, chain["emp"].email)
    req = _apply_leave(client, emp_headers, lt.id)
    assert req["current_approver_id"] == chain["tl"].id


def test_team_lead_routes_to_manager(client, db_session):
    chain = _build_chain(db_session, "chain2")
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, chain["tl"], lt, next_monday().year, 10)
    tl_headers = login_headers(client, chain["tl"].email)
    req = _apply_leave(client, tl_headers, lt.id)
    assert req["current_approver_id"] == chain["mgr"].id


def test_manager_routes_to_senior_manager(client, db_session):
    chain = _build_chain(db_session, "chain3")
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, chain["mgr"], lt, next_monday().year, 10)
    mgr_headers = login_headers(client, chain["mgr"].email)
    req = _apply_leave(client, mgr_headers, lt.id)
    assert req["current_approver_id"] == chain["sr_mgr"].id


def test_senior_manager_routes_to_director(client, db_session):
    chain = _build_chain(db_session, "chain4")
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, chain["sr_mgr"], lt, next_monday().year, 10)
    sr_headers = login_headers(client, chain["sr_mgr"].email)
    req = _apply_leave(client, sr_headers, lt.id)
    assert req["current_approver_id"] == chain["director"].id


def test_director_routes_to_ceo(client, db_session):
    chain = _build_chain(db_session, "chain5")
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, chain["director"], lt, next_monday().year, 10)
    dir_headers = login_headers(client, chain["director"].email)
    req = _apply_leave(client, dir_headers, lt.id)
    assert req["current_approver_id"] == chain["ceo"].id


def test_hr_associate_routes_to_hr_manager(client, db_session):
    hr = _build_hr_chain(db_session, "hrchain1")
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, hr["hr_assoc"], lt, next_monday().year, 10)
    headers = login_headers(client, hr["hr_assoc"].email)
    req = _apply_leave(client, headers, lt.id)
    assert req["current_approver_id"] == hr["hr_mgr"].id


def test_hr_manager_routes_to_hr_director(client, db_session):
    hr = _build_hr_chain(db_session, "hrchain2")
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, hr["hr_mgr"], lt, next_monday().year, 10)
    headers = login_headers(client, hr["hr_mgr"].email)
    req = _apply_leave(client, headers, lt.id)
    assert req["current_approver_id"] == hr["hr_dir"].id


def test_hr_director_routes_to_ceo(client, db_session):
    hr = _build_hr_chain(db_session, "hrchain3")
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, hr["hr_dir"], lt, next_monday().year, 10)
    headers = login_headers(client, hr["hr_dir"].email)
    req = _apply_leave(client, headers, lt.id)
    assert req["current_approver_id"] == hr["ceo"].id


def test_ceo_auto_approval_in_chain(client, db_session):
    chain = _build_chain(db_session, "chain6")
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, chain["ceo"], lt, next_monday().year, 10)
    headers = login_headers(client, chain["ceo"].email)
    req = _apply_leave(client, headers, lt.id)
    assert req["status"] == "APPROVED"
    assert req["current_approver_id"] is None


def test_correct_approver_can_approve(client, db_session):
    chain = _build_chain(db_session, "chain7")
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, chain["emp"], lt, next_monday().year, 10)
    emp_headers = login_headers(client, chain["emp"].email)
    req = _apply_leave(client, emp_headers, lt.id)

    tl_headers = login_headers(client, chain["tl"].email)
    resp = client.post(f"/api/approvals/{req['id']}/approve", headers=tl_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "APPROVED"


def test_wrong_approver_cannot_approve(client, db_session):
    """A random manager must not be able to approve another manager's assigned request."""
    chain = _build_chain(db_session, "chain8")
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, chain["emp"], lt, next_monday().year, 10)
    emp_headers = login_headers(client, chain["emp"].email)
    req = _apply_leave(client, emp_headers, lt.id)

    # A different manager, not in this employee's chain
    random_mgr = make_employee(db_session, "Random Mgr", "randommgr8@company.com", Role.MANAGER)
    random_headers = login_headers(client, "randommgr8@company.com")
    resp = client.post(f"/api/approvals/{req['id']}/approve", headers=random_headers)
    assert resp.status_code == 403


def test_unauthorized_role_cannot_approve(client, db_session):
    chain = _build_chain(db_session, "chain9")
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, chain["emp"], lt, next_monday().year, 10)
    emp_headers = login_headers(client, chain["emp"].email)
    req = _apply_leave(client, emp_headers, lt.id)

    resp = client.post(f"/api/approvals/{req['id']}/approve", headers=emp_headers)
    assert resp.status_code == 403


def test_rejection_reason_required(client, db_session):
    chain = _build_chain(db_session, "chain10")
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, chain["emp"], lt, next_monday().year, 10)
    emp_headers = login_headers(client, chain["emp"].email)
    req = _apply_leave(client, emp_headers, lt.id)

    tl_headers = login_headers(client, chain["tl"].email)
    resp = client.post(f"/api/approvals/{req['id']}/reject", json={"reason": ""}, headers=tl_headers)
    assert resp.status_code == 422


def test_reject_with_reason_succeeds(client, db_session):
    chain = _build_chain(db_session, "chain11")
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, chain["emp"], lt, next_monday().year, 10)
    emp_headers = login_headers(client, chain["emp"].email)
    req = _apply_leave(client, emp_headers, lt.id)

    tl_headers = login_headers(client, chain["tl"].email)
    resp = client.post(
        f"/api/approvals/{req['id']}/reject", json={"reason": "Team is short-staffed that week"}, headers=tl_headers
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "REJECTED"


def test_approval_deducts_balance(client, db_session):
    chain = _build_chain(db_session, "chain12")
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, chain["emp"], lt, next_monday().year, 10)
    emp_headers = login_headers(client, chain["emp"].email)
    req = _apply_leave(client, emp_headers, lt.id)

    tl_headers = login_headers(client, chain["tl"].email)
    client.post(f"/api/approvals/{req['id']}/approve", headers=tl_headers)

    balance = client.get(f"/api/leave-balances/me?year={next_monday().year}", headers=emp_headers).json()[0]
    assert balance["used_days"] == 1


def test_approval_creates_notification(client, db_session):
    chain = _build_chain(db_session, "chain13")
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, chain["emp"], lt, next_monday().year, 10)
    emp_headers = login_headers(client, chain["emp"].email)
    req = _apply_leave(client, emp_headers, lt.id)

    tl_headers = login_headers(client, chain["tl"].email)
    client.post(f"/api/approvals/{req['id']}/approve", headers=tl_headers)

    notifications = client.get("/api/notifications", headers=emp_headers).json()
    assert any(n["notification_type"] == "LEAVE_REQUEST_APPROVED" for n in notifications)


def test_submission_creates_notification_for_approver(client, db_session):
    chain = _build_chain(db_session, "chain14")
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, chain["emp"], lt, next_monday().year, 10)
    emp_headers = login_headers(client, chain["emp"].email)
    _apply_leave(client, emp_headers, lt.id)

    tl_headers = login_headers(client, chain["tl"].email)
    notifications = client.get("/api/notifications", headers=tl_headers).json()
    assert any(n["notification_type"] == "LEAVE_REQUEST_SUBMITTED" for n in notifications)


def test_approval_history_recorded(client, db_session):
    chain = _build_chain(db_session, "chain15")
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, chain["emp"], lt, next_monday().year, 10)
    emp_headers = login_headers(client, chain["emp"].email)
    req = _apply_leave(client, emp_headers, lt.id)

    tl_headers = login_headers(client, chain["tl"].email)
    client.post(f"/api/approvals/{req['id']}/approve", headers=tl_headers)

    history = client.get(f"/api/approvals/{req['id']}/history", headers=emp_headers).json()
    assert len(history) == 1
    assert history[0]["action"] == "APPROVED"
    assert history[0]["approver_id"] == chain["tl"].id


def test_cannot_approve_already_approved_request(client, db_session):
    chain = _build_chain(db_session, "chain16")
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, chain["emp"], lt, next_monday().year, 10)
    emp_headers = login_headers(client, chain["emp"].email)
    req = _apply_leave(client, emp_headers, lt.id)

    tl_headers = login_headers(client, chain["tl"].email)
    client.post(f"/api/approvals/{req['id']}/approve", headers=tl_headers)
    resp = client.post(f"/api/approvals/{req['id']}/approve", headers=tl_headers)
    assert resp.status_code == 422


def test_inactive_approver_blocks_submission(client, db_session):
    chain = _build_chain(db_session, "chain17")
    lt = make_leave_type(db_session, "Paid Leave")
    set_balance(db_session, chain["emp"], lt, next_monday().year, 10)

    chain["tl"].is_active = False
    db_session.commit()

    emp_headers = login_headers(client, chain["emp"].email)
    monday = next_monday()
    resp = client.post(
        "/api/leave-requests",
        json={"leave_type_id": lt.id, "start_date": str(monday), "end_date": str(monday), "explanation": "X"},
        headers=emp_headers,
    )
    assert resp.status_code == 422
    assert "inactive" in resp.json()["detail"].lower()
