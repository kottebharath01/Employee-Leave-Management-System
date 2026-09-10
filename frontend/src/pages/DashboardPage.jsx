import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";
import { isApprover, isHr, isAdmin } from "../roles";

export default function DashboardPage() {
  const { user } = useAuth();
  const [balances, setBalances] = useState([]);
  const [myRequests, setMyRequests] = useState([]);
  const [pendingApprovals, setPendingApprovals] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    api.get("/leave-balances/me").then((res) => setBalances(res.data)).catch(() => {});
    api.get("/leave-requests/me").then((res) => setMyRequests(res.data)).catch(() => {});
    api.get("/notifications?unread_only=true").then((res) => setUnreadCount(res.data.length)).catch(() => {});
    if (isApprover(user)) {
      api.get("/approvals/pending").then((res) => setPendingApprovals(res.data)).catch(() => {});
    }
  }, [user]);

  const pendingCount = myRequests.filter((r) => r.status === "PENDING").length;

  return (
    <div>
      <h1>Welcome, {user?.name}</h1>
      <p className="subtitle">
        Role: {user?.role} {user?.is_admin && "• Admin"}
      </p>

      <div className="dashboard-grid">
        <div className="card stat-card">
          <h3>My Leave Balance</h3>
          {balances.length === 0 && <p>No balance records yet.</p>}
          {balances.map((b) => (
            <div key={b.id} className="balance-row">
              <span>Leave Type #{b.leave_type_id}</span>
              <span>
                {b.available_days} / {b.total_days} days left
              </span>
            </div>
          ))}
          <Link to="/leave-requests/new" className="btn btn-primary btn-block">
            Apply for Leave
          </Link>
        </div>

        <div className="card stat-card">
          <h3>My Requests</h3>
          <p className="big-number">{myRequests.length}</p>
          <p>{pendingCount} pending</p>
          <Link to="/leave-requests" className="btn btn-secondary btn-block">
            View My Requests
          </Link>
        </div>

        {isApprover(user) && (
          <div className="card stat-card">
            <h3>Pending Approvals</h3>
            <p className="big-number">{pendingApprovals.length}</p>
            <Link to="/approvals" className="btn btn-secondary btn-block">
              Review Requests
            </Link>
          </div>
        )}

        <div className="card stat-card">
          <h3>Notifications</h3>
          <p className="big-number">{unreadCount}</p>
          <p>unread</p>
          <Link to="/notifications" className="btn btn-secondary btn-block">
            View Notifications
          </Link>
        </div>

        {isHr(user) && (
          <div className="card stat-card">
            <h3>HR Tools</h3>
            <p>Manage employees, leave types, balances, and holidays.</p>
            <Link to="/hr" className="btn btn-secondary btn-block">
              Go to HR Panel
            </Link>
          </div>
        )}

        {isAdmin(user) && (
          <div className="card stat-card">
            <h3>Admin Tools</h3>
            <p>Manage system users, roles, and account status.</p>
            <Link to="/admin" className="btn btn-secondary btn-block">
              Go to Admin Panel
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
