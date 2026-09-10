import { useEffect, useState } from "react";
import api, { getErrorMessage } from "../../api/client";

export default function HolidaysTab() {
  const [holidays, setHolidays] = useState([]);
  const [error, setError] = useState("");
  const [form, setForm] = useState({ holiday_date: "", name: "", description: "" });

  const load = () => {
    api
      .get("/holidays")
      .then((res) => setHolidays(res.data))
      .catch((err) => setError(getErrorMessage(err)));
  };

  useEffect(load, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.post("/holidays", form);
      setForm({ holiday_date: "", name: "", description: "" });
      load();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  const handleDelete = async (id) => {
    try {
      await api.delete(`/holidays/${id}`);
      load();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  return (
    <div>
      <h2>Company Holidays</h2>
      {error && <div className="alert alert-error">{error}</div>}

      <form className="card form-card" onSubmit={handleCreate}>
        <div className="form-row">
          <label>
            Date
            <input
              type="date"
              required
              value={form.holiday_date}
              onChange={(e) => setForm({ ...form, holiday_date: e.target.value })}
            />
          </label>
          <label>
            Name
            <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          </label>
        </div>
        <button className="btn btn-primary" type="submit">
          Add Holiday
        </button>
      </form>

      <table className="data-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Name</th>
            <th>Active</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {holidays.map((h) => (
            <tr key={h.id}>
              <td>{h.holiday_date}</td>
              <td>{h.name}</td>
              <td>{h.is_active ? "Active" : "Inactive"}</td>
              <td>
                <button className="btn btn-small btn-danger" onClick={() => handleDelete(h.id)}>
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
