import { useState } from "react";
import api, { getErrorMessage } from "../../api/client";

export default function LeaveBalancesTab() {
  const [employeeId, setEmployeeId] = useState("");
  const [leaveTypeId, setLeaveTypeId] = useState("");
  const [year, setYear] = useState(new Date().getFullYear());
  const [totalDays, setTotalDays] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [lookupEmployeeId, setLookupEmployeeId] = useState("");
  const [lookupResults, setLookupResults] = useState([]);

  const handleSet = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    try {
      await api.put("/leave-balances", {
        employee_id: Number(employeeId),
        leave_type_id: Number(leaveTypeId),
        year: Number(year),
        total_days: Number(totalDays),
      });
      setSuccess("Balance updated successfully.");
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  const handleLookup = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const res = await api.get(`/leave-balances/employee/${lookupEmployeeId}?year=${year}`);
      setLookupResults(res.data);
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  return (
    <div>
      <h2>Leave Balances</h2>
      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <form className="card form-card" onSubmit={handleSet}>
        <h3>Set / Update Balance</h3>
        <div className="form-row">
          <label>
            Employee ID
            <input type="number" required value={employeeId} onChange={(e) => setEmployeeId(e.target.value)} />
          </label>
          <label>
            Leave Type ID
            <input type="number" required value={leaveTypeId} onChange={(e) => setLeaveTypeId(e.target.value)} />
          </label>
        </div>
        <div className="form-row">
          <label>
            Year
            <input type="number" required value={year} onChange={(e) => setYear(e.target.value)} />
          </label>
          <label>
            Total Days
            <input type="number" required min={0} value={totalDays} onChange={(e) => setTotalDays(e.target.value)} />
          </label>
        </div>
        <button className="btn btn-primary" type="submit">
          Save Balance
        </button>
      </form>

      <form className="card form-card" onSubmit={handleLookup}>
        <h3>Look Up Employee Balances</h3>
        <div className="form-row">
          <label>
            Employee ID
            <input
              type="number"
              required
              value={lookupEmployeeId}
              onChange={(e) => setLookupEmployeeId(e.target.value)}
            />
          </label>
        </div>
        <button className="btn btn-secondary" type="submit">
          Look Up
        </button>
      </form>

      {lookupResults.length > 0 && (
        <table className="data-table">
          <thead>
            <tr>
              <th>Leave Type ID</th>
              <th>Year</th>
              <th>Total</th>
              <th>Used</th>
              <th>Available</th>
            </tr>
          </thead>
          <tbody>
            {lookupResults.map((b) => (
              <tr key={b.id}>
                <td>{b.leave_type_id}</td>
                <td>{b.year}</td>
                <td>{b.total_days}</td>
                <td>{b.used_days}</td>
                <td>{b.available_days}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
