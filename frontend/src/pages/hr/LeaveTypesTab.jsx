import { useEffect, useState } from "react";
import api, { getErrorMessage } from "../../api/client";

export default function LeaveTypesTab() {
  const [leaveTypes, setLeaveTypes] = useState([]);
  const [error, setError] = useState("");
  const [form, setForm] = useState({ name: "", description: "", is_paid: true });

  const load = () => {
    api
      .get("/leave-types")
      .then((res) => setLeaveTypes(res.data))
      .catch((err) => setError(getErrorMessage(err)));
  };

  useEffect(load, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.post("/leave-types", form);
      setForm({ name: "", description: "", is_paid: true });
      load();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  const toggleActive = async (lt) => {
    try {
      await api.put(`/leave-types/${lt.id}`, { is_active: !lt.is_active });
      load();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  return (
    <div>
      <h2>Leave Types</h2>
      {error && <div className="alert alert-error">{error}</div>}

      <form className="card form-card" onSubmit={handleCreate}>
        <div className="form-row">
          <label>
            Name
            <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          </label>
          <label>
            Description
            <input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={form.is_paid}
              onChange={(e) => setForm({ ...form, is_paid: e.target.checked })}
            />
            Paid leave type
          </label>
        </div>
        <button className="btn btn-primary" type="submit">
          Add Leave Type
        </button>
      </form>

      <table className="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Paid?</th>
            <th>Active</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {leaveTypes.map((lt) => (
            <tr key={lt.id}>
              <td>{lt.id}</td>
              <td>{lt.name}</td>
              <td>{lt.is_paid ? "Yes" : "No"}</td>
              <td>{lt.is_active ? "Active" : "Inactive"}</td>
              <td>
                <button className="btn btn-small btn-secondary" onClick={() => toggleActive(lt)}>
                  {lt.is_active ? "Deactivate" : "Activate"}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
