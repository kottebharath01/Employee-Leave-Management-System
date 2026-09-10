import { useEffect, useState } from "react";
import api, { getErrorMessage } from "../api/client";

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState([]);
  const [error, setError] = useState("");

  const load = () => {
    api
      .get("/notifications")
      .then((res) => setNotifications(res.data))
      .catch((err) => setError(getErrorMessage(err)));
  };

  useEffect(load, []);

  const markRead = async (id) => {
    try {
      await api.patch(`/notifications/${id}/read`);
      load();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  return (
    <div>
      <h1>Notifications</h1>
      {error && <div className="alert alert-error">{error}</div>}
      <div className="notification-list">
        {notifications.map((n) => (
          <div key={n.id} className={`notification-item ${n.is_read ? "" : "unread"}`}>
            <div>
              <strong>{n.notification_type.replace(/_/g, " ")}</strong>
              <p>{n.message}</p>
              <span className="hint">{new Date(n.created_at).toLocaleString()}</span>
            </div>
            {!n.is_read && (
              <button className="btn btn-small btn-secondary" onClick={() => markRead(n.id)}>
                Mark read
              </button>
            )}
          </div>
        ))}
        {notifications.length === 0 && <p>No notifications yet.</p>}
      </div>
    </div>
  );
}
