import { useEffect, useState } from "react";
import api, { getErrorMessage } from "../../api/client";
import { ROLES } from "../../roles";

export default function EmployeesTab() {
  const [employees, setEmployees] = useState([]);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    role: ROLES.EMPLOYEE,
    manager_id: "",
    is_admin: false,
  });

  const load = () => {
    api
      .get("/employees")
      .then((res) => setEmployees(res.data))
      .catch((err) => setError(getErrorMessage(err)));
  };

  useEffect(load, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.post("/employees", {
        ...form,
        manager_id: form.manager_id ? Number(form.manager_id) : null,
      });
      setShowForm(false);
      setForm({ name: "", email: "", password: "", role: ROLES.EMPLOYEE, manager_id: "", is_admin: false });
      load();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  const toggleActive = async (emp) => {
    try {
      await api.patch(`/employees/${emp.id}/${emp.is_active ? "deactivate" : "activate"}`);
      load();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  return (
    <div>
      <div className="page-header">
        <h2>Employees</h2>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? "Cancel" : "+ New Employee"}
        </button>
      </div>
      {error && <div className="alert alert-error">{error}</div>}

      {showForm && (
        <form className="card form-card" onSubmit={handleCreate}>
          <div className="form-row">
            <label>
              Name
              <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
            </label>
            <label>
              Email
              <input
                type="email"
                required
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
              />
            </label>
          </div>
          <div className="form-row">
            <label>
              Temporary Password
              <input
                type="text"
                required
                minLength={8}
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
              />
            </label>
            <label>
              Role
              <select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
                {Object.values(ROLES)
                  .filter((r) => r !== ROLES.ADMIN)
                  .map((r) => (
                    <option key={r} value={r}>
                      {r}
                    </option>
                  ))}
              </select>
            </label>
          </div>
          <div className="form-row">
            <label>
              Manager ID (optional)
              <input
                type="number"
                value={form.manager_id}
                onChange={(e) => setForm({ ...form, manager_id: e.target.value })}
              />
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={form.is_admin}
                onChange={(e) => setForm({ ...form, is_admin: e.target.checked })}
              />
              Grant Admin access
            </label>
          </div>
          <button className="btn btn-primary" type="submit">
            Create Employee
          </button>
        </form>
      )}

      <table className="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Manager ID</th>
            <th>Admin</th>
            <th>Active</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {employees.map((e) => (
            <tr key={e.id}>
              <td>{e.id}</td>
              <td>{e.name}</td>
              <td>{e.email}</td>
              <td>{e.role}</td>
              <td>{e.manager_id ?? "—"}</td>
              <td>{e.is_admin ? "Yes" : "No"}</td>
              <td>{e.is_active ? "Active" : "Inactive"}</td>
              <td>
                <button className="btn btn-small btn-secondary" onClick={() => toggleActive(e)}>
                  {e.is_active ? "Deactivate" : "Activate"}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
