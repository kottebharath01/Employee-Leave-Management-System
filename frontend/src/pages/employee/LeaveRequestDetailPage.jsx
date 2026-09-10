import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api, { getErrorMessage } from "../../api/client";

export default function LeaveRequestDetailPage() {
  const { id } = useParams();
  const [request, setRequest] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get(`/leave-requests/${id}`)
      .then((res) => setRequest(res.data))
      .catch((err) => setError(getErrorMessage(err)));
    api
      .get(`/approvals/${id}/history`)
      .then((res) => setHistory(res.data))
      .catch(() => {});
  }, [id]);

  if (error) return <div className="alert alert-error">{error}</div>;
  if (!request) return <p>Loading...</p>;

  return (
    <div className="card">
      <h1>Leave Request #{request.id}</h1>
      <table className="detail-table">
        <tbody>
          <tr>
            <td>Status</td>
            <td>{request.status}</td>
          </tr>
          <tr>
            <td>Dates</td>
            <td>
              {request.start_date} to {request.end_date}
            </td>
          </tr>
          <tr>
            <td>Paid / Unpaid days</td>
            <td>
              {request.paid_days} / {request.unpaid_days}
            </td>
          </tr>
          <tr>
            <td>Explanation</td>
            <td>{request.explanation}</td>
          </tr>
        </tbody>
      </table>

      <h2>Approval History</h2>
      <table className="data-table">
        <thead>
          <tr>
            <th>Action</th>
            <th>Approver ID</th>
            <th>Reason</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {history.map((h) => (
            <tr key={h.id}>
              <td>{h.action}</td>
              <td>{h.approver_id ?? "—"}</td>
              <td>{h.reason || "—"}</td>
              <td>{new Date(h.timestamp).toLocaleString()}</td>
            </tr>
          ))}
          {history.length === 0 && (
            <tr>
              <td colSpan={4}>No history yet.</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
