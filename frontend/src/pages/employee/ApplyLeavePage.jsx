import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api, { getErrorMessage } from "../../api/client";

export default function ApplyLeavePage() {
  const [leaveTypes, setLeaveTypes] = useState([]);
  const [leaveTypeId, setLeaveTypeId] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [explanation, setExplanation] = useState("");
  const [preview, setPreview] = useState(null);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    api
      .get("/leave-types?is_active=true")
      .then((res) => {
        setLeaveTypes(res.data);
        if (res.data.length > 0) setLeaveTypeId(String(res.data[0].id));
      })
      .catch((err) => setError(getErrorMessage(err)));
  }, []);

  const canPreview = leaveTypeId && startDate && endDate;

  const handlePreview = async () => {
    setError("");
    setPreview(null);
    try {
      const res = await api.post("/leave-requests/preview", {
        leave_type_id: Number(leaveTypeId),
        start_date: startDate,
        end_date: endDate,
      });
      setPreview(res.data);
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  const handleSubmit = async (confirmUnpaid) => {
    if (!explanation.trim()) {
      setError("Please provide an explanation for your leave request.");
      return;
    }
    setSubmitting(true);
    setError("");
    try {
      await api.post("/leave-requests", {
        leave_type_id: Number(leaveTypeId),
        start_date: startDate,
        end_date: endDate,
        explanation,
        confirm_unpaid: confirmUnpaid,
      });
      navigate("/leave-requests");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="card form-card">
      <h1>Apply for Leave</h1>
      {error && <div className="alert alert-error">{error}</div>}

      <label>
        Leave Type
        <select value={leaveTypeId} onChange={(e) => { setLeaveTypeId(e.target.value); setPreview(null); }}>
          {leaveTypes.map((lt) => (
            <option key={lt.id} value={lt.id}>
              {lt.name} {lt.is_paid ? "(Paid)" : "(Unpaid)"}
            </option>
          ))}
        </select>
      </label>

      <div className="form-row">
        <label>
          Start Date
          <input
            type="date"
            value={startDate}
            onChange={(e) => { setStartDate(e.target.value); setPreview(null); }}
          />
        </label>
        <label>
          End Date
          <input type="date" value={endDate} onChange={(e) => { setEndDate(e.target.value); setPreview(null); }} />
        </label>
      </div>

      <label>
        Explanation
        <textarea
          rows={3}
          value={explanation}
          onChange={(e) => setExplanation(e.target.value)}
          placeholder="Reason for leave..."
        />
      </label>

      {!preview && (
        <button className="btn btn-secondary" disabled={!canPreview} onClick={handlePreview}>
          Check Availability
        </button>
      )}

      {preview && (
        <div className="alert alert-info">
          <p>{preview.message}</p>
          <p>
            Working days: {preview.working_days} • Paid: {preview.paid_days} • Unpaid: {preview.unpaid_days}
          </p>
          {preview.requires_confirmation ? (
            <div className="button-row">
              <button className="btn btn-primary" disabled={submitting} onClick={() => handleSubmit(true)}>
                Yes, continue with {preview.unpaid_days} unpaid day(s)
              </button>
              <button className="btn btn-secondary" onClick={() => setPreview(null)}>
                No, change dates
              </button>
            </div>
          ) : (
            <button className="btn btn-primary" disabled={submitting} onClick={() => handleSubmit(false)}>
              {submitting ? "Submitting..." : "Submit Leave Request"}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
