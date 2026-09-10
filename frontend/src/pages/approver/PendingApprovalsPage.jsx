import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api, { getErrorMessage } from "../../api/client";

export default function PendingApprovalsPage() {
  const [requests, setRequests] = useState([]);
  const [error, setError] = useState("");
  const [rejectingId, setRejectingId] = useState(null);
  const [rejectReason, setRejectReason] = useState("");
  const [busyId, setBusyId] = useState(null);

  const load = () => {
    api
      .get("/approvals/pending")
      .then((res) => setRequests(res.data))
      .catch((err) => setError(getErrorMessage(err)));
  };

  useEffect(load, []);

  const handleApprove = async (id) => {
    setBusyId(id);
    setError("");
    try {
      await api.post(`/approvals/${id}/approve`);
      load();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setBusyId(null);
    }
  };

  const openReject = (id) => {
    setRejectingId(id);
    setRejectReason("");
  };

  const submitReject = async () => {
    if (!rejectReason.trim()) {
      setError("A rejection reason is required.");
      return;
    }
    setBusyId(rejectingId);
    setError("");
    try {
      await api.post(`/approvals/${rejectingId}/reject`, { reason: rejectReason });
      setRejectingId(null);
      load();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setBusyId(null);
    }
  };

  return (
    <div>
      <h1>Pending Approvals</h1>
      {error && <div className="alert alert-error">{error}</div>}

      <table className="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Employee ID</th>
            <th>Dates</th>
            <th>Paid / Unpaid</th>
            <th>Explanation</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {requests.map((r) => (
            <tr key={r.id}>
              <td>
                <Link to={`/leave-requests/${r.id}`}>#{r.id}</Link>
              </td>
              <td>{r.employee_id}</td>
              <td>
                {r.start_date} to {r.end_date}
              </td>
              <td>
                {r.paid_days} / {r.unpaid_days}
              </td>
              <td>{r.explanation}</td>
              <td>
                <button
                  className="btn btn-small btn-primary"
                  disabled={busyId === r.id}
                  onClick={() => handleApprove(r.id)}
                >
                  Approve
                </button>
                <button className="btn btn-small btn-danger" disabled={busyId === r.id} onClick={() => openReject(r.id)}>
                  Reject
                </button>
              </td>
            </tr>
          ))}
          {requests.length === 0 && (
            <tr>
              <td colSpan={6}>No pending requests assigned to you.</td>
            </tr>
          )}
        </tbody>
      </table>

      {rejectingId && (
        <div className="modal-backdrop">
          <div className="card modal">
            <h3>Reject Request #{rejectingId}</h3>
            <label>
              Rejection reason (required)
              <textarea rows={3} value={rejectReason} onChange={(e) => setRejectReason(e.target.value)} />
            </label>
            <div className="button-row">
              <button className="btn btn-danger" onClick={submitReject}>
                Confirm Rejection
              </button>
              <button className="btn btn-secondary" onClick={() => setRejectingId(null)}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
