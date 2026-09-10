import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { isApprover, isHr, isAdmin } from "../roles";

export default function ProtectedRoute({ children, requireApprover, requireHr, requireAdmin }) {
  const { user, loading } = useAuth();

  if (loading) return <div className="page-loading">Loading...</div>;
  if (!user) return <Navigate to="/login" replace />;

  if (requireApprover && !isApprover(user)) return <Navigate to="/dashboard" replace />;
  if (requireHr && !isHr(user)) return <Navigate to="/dashboard" replace />;
  if (requireAdmin && !isAdmin(user)) return <Navigate to="/dashboard" replace />;

  return children;
}
