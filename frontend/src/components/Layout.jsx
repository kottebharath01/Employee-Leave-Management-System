import { Link, useNavigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { isApprover, isHr, isAdmin } from "../roles";

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="app-header-left">
          <Link to="/dashboard" className="app-title">
            Leave Manager
          </Link>
          <nav className="app-nav">
            <Link to="/dashboard">Dashboard</Link>
            <Link to="/leave-requests">My Requests</Link>
            <Link to="/leave-requests/new">Apply Leave</Link>
            {isApprover(user) && <Link to="/approvals">Approvals</Link>}
            {isHr(user) && <Link to="/hr">HR</Link>}
            {isAdmin(user) && <Link to="/admin">Admin</Link>}
            <Link to="/notifications">Notifications</Link>
          </nav>
        </div>
        <div className="app-header-right">
          {user && (
            <span className="user-badge">
              {user.name} ({user.role})
            </span>
          )}
          <button className="btn btn-secondary" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </header>
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
}
