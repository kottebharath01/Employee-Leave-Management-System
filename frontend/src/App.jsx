import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Layout from "./components/Layout";

import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import NotificationsPage from "./pages/NotificationsPage";

import MyLeaveRequestsPage from "./pages/employee/MyLeaveRequestsPage";
import ApplyLeavePage from "./pages/employee/ApplyLeavePage";
import EditLeaveRequestPage from "./pages/employee/EditLeaveRequestPage";
import LeaveRequestDetailPage from "./pages/employee/LeaveRequestDetailPage";

import PendingApprovalsPage from "./pages/approver/PendingApprovalsPage";

import HrPage from "./pages/hr/HrPage";
import AdminPage from "./pages/admin/AdminPage";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          <Route
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/notifications" element={<NotificationsPage />} />

            <Route path="/leave-requests" element={<MyLeaveRequestsPage />} />
            <Route path="/leave-requests/new" element={<ApplyLeavePage />} />
            <Route path="/leave-requests/:id" element={<LeaveRequestDetailPage />} />
            <Route path="/leave-requests/:id/edit" element={<EditLeaveRequestPage />} />

            <Route
              path="/approvals"
              element={
                <ProtectedRoute requireApprover>
                  <PendingApprovalsPage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/hr"
              element={
                <ProtectedRoute requireHr>
                  <HrPage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/admin"
              element={
                <ProtectedRoute requireAdmin>
                  <AdminPage />
                </ProtectedRoute>
              }
            />
          </Route>

          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
