import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api, { getErrorMessage } from "../../api/client";

const STATUS_COLORS = {
  PENDING: "badge-pending",
  APPROVED: "badge-approved",
  REJECTED: "badge-rejected",
  CANCELLED: "badge-cancelled",
};

export default function MyLeaveRequestsPage() {
  const [requests, setRequests] = useState([]);
  const [error, setError] = useState("");
  const [cancellingId, setCancellingId] = useState(null);

  const load = () => {
    api
      .get("/leave-requests/me")
      .then((res) => setRequests(res.data))
      .catch((err) => setError(getErrorMessage(err)));
  };

  useEffect(load, []);

  const handleCancel = async (id) => {
    setCancellingId(id);
    setError("");
    try {
      await api.post(`/leave-requests/${id}/cancel`);
      load();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setCancellingId(null);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1>My Leave Requests</h1>
        <Link to="/leave-requests/new" className="btn btn-primary">
          Apply for Leave
        </Link>
      </div>
      {error && <div className="alert alert-error">{error}</div>}

      <table className="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Dates</th>
            <th>Paid / Unpaid</th>
            <th>Status</th>
            <th>Explanation</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {requests.map((r) => (
            <tr key={r.id}>
              <td>#{r.id}</td>
              <td>
                {r.start_date} to {r.end_date}
              </td>
              <td>
                {r.paid_days} / {r.unpaid_days}
              </td>
              <td>
                <span className={`badge ${STATUS_COLORS[r.status] || ""}`}>{r.status}</span>
              </td>
              <td>{r.explanation}</td>
              <td>
                {(r.status === "PENDING" || r.status === "APPROVED") && (
                  <button
                    className="btn btn-small btn-danger"
                    disabled={cancellingId === r.id}
                    onClick={() => handleCancel(r.id)}
                  >
                    Cancel
                  </button>
                )}
                {r.status === "PENDING" && (
                  <Link className="btn btn-small btn-secondary" to={`/leave-requests/${r.id}/edit`}>
                    Edit
                  </Link>
                )}
              </td>
            </tr>
          ))}
          {requests.length === 0 && (
            <tr>
              <td colSpan={6}>No leave requests yet.</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
