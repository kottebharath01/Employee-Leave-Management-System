from app.core.enums import Role, NotificationType
from app.services import notification_service
from tests.conftest import make_employee, login_headers


def test_notification_recipient_correct(client, db_session):
    emp = make_employee(db_session, "NotifOwner", "notifowner@company.com", Role.EMPLOYEE)
    other = make_employee(db_session, "NotifOther", "notifother@company.com", Role.EMPLOYEE)
    notification_service.create_notification(db_session, emp.id, NotificationType.LEAVE_REQUEST_APPROVED, "Test msg")

    owner_headers = login_headers(client, "notifowner@company.com")
    other_headers = login_headers(client, "notifother@company.com")

    owner_notifs = client.get("/api/notifications", headers=owner_headers).json()
    other_notifs = client.get("/api/notifications", headers=other_headers).json()

    assert len(owner_notifs) == 1
    assert len(other_notifs) == 0


def test_notification_starts_unread(client, db_session):
    emp = make_employee(db_session, "UnreadOwner", "unreadowner@company.com", Role.EMPLOYEE)
    notification_service.create_notification(db_session, emp.id, NotificationType.LEAVE_REQUEST_APPROVED, "Test msg")
    headers = login_headers(client, "unreadowner@company.com")
    notifs = client.get("/api/notifications", headers=headers).json()
    assert notifs[0]["is_read"] is False


def test_mark_notification_read(client, db_session):
    emp = make_employee(db_session, "ReadOwner", "readowner@company.com", Role.EMPLOYEE)
    n = notification_service.create_notification(db_session, emp.id, NotificationType.LEAVE_REQUEST_APPROVED, "Test")
    headers = login_headers(client, "readowner@company.com")
    resp = client.patch(f"/api/notifications/{n.id}/read", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["is_read"] is True


def test_cannot_mark_others_notification_read(client, db_session):
    emp = make_employee(db_session, "OwnerX", "ownerx@company.com", Role.EMPLOYEE)
    other = make_employee(db_session, "OtherX", "otherx@company.com", Role.EMPLOYEE)
    n = notification_service.create_notification(db_session, emp.id, NotificationType.LEAVE_REQUEST_APPROVED, "Test")
    other_headers = login_headers(client, "otherx@company.com")
    resp = client.patch(f"/api/notifications/{n.id}/read", headers=other_headers)
    assert resp.status_code == 403


def test_unread_only_filter(client, db_session):
    emp = make_employee(db_session, "FilterOwner", "filterowner@company.com", Role.EMPLOYEE)
    n1 = notification_service.create_notification(db_session, emp.id, NotificationType.LEAVE_REQUEST_APPROVED, "One")
    notification_service.create_notification(db_session, emp.id, NotificationType.LEAVE_REQUEST_REJECTED, "Two")
    headers = login_headers(client, "filterowner@company.com")
    client.patch(f"/api/notifications/{n1.id}/read", headers=headers)

    unread = client.get("/api/notifications?unread_only=true", headers=headers).json()
    assert len(unread) == 1
    assert unread[0]["message"] == "Two"
