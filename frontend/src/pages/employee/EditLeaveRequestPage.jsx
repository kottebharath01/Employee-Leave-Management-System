import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api, { getErrorMessage } from "../../api/client";

export default function EditLeaveRequestPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [explanation, setExplanation] = useState("");
  const [error, setError] = useState("");
  const [needsConfirm, setNeedsConfirm] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    api.get(`/leave-requests/${id}`).then((res) => {
      setStartDate(res.data.start_date);
      setEndDate(res.data.end_date);
      setExplanation(res.data.explanation);
    });
  }, [id]);

  const handleSubmit = async (confirmUnpaid = false) => {
    setSubmitting(true);
    setError("");
    setNeedsConfirm(false);
    try {
      await api.put(`/leave-requests/${id}`, {
        start_date: startDate,
        end_date: endDate,
        explanation,
        confirm_unpaid: confirmUnpaid,
      });
      navigate("/leave-requests");
    } catch (err) {
      const msg = getErrorMessage(err);
      setError(msg);
      if (msg.toLowerCase().includes("unpaid")) {
        setNeedsConfirm(true);
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="card form-card">
      <h1>Edit Leave Request #{id}</h1>
      <p className="hint">Only PENDING requests can be edited.</p>
      {error && <div className="alert alert-error">{error}</div>}

      <div className="form-row">
        <label>
          Start Date
          <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
        </label>
        <label>
          End Date
          <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
        </label>
      </div>

      <label>
        Explanation
        <textarea rows={3} value={explanation} onChange={(e) => setExplanation(e.target.value)} />
      </label>

      <div className="button-row">
        <button className="btn btn-primary" disabled={submitting} onClick={() => handleSubmit(false)}>
          Save Changes
        </button>
        {needsConfirm && (
          <button className="btn btn-secondary" disabled={submitting} onClick={() => handleSubmit(true)}>
            Confirm with Unpaid Days
          </button>
        )}
      </div>
    </div>
  );
}
