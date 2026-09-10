import { useEffect, useState } from "react";
import api, { getErrorMessage } from "../../api/client";

export default function AdminPage() {
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [error, setError] = useState("");

  const load = () => {
    api
      .get("/admin/users")
      .then((res) => setUsers(res.data))
      .catch((err) => setError(getErrorMessage(err)));
    api
      .get("/admin/roles")
      .then((res) => setRoles(res.data.roles))
      .catch(() => {});
  };

  useEffect(load, []);

  const toggleActive = async (user) => {
    try {
      await api.patch(`/admin/users/${user.id}/${user.is_active ? "deactivate" : "activate"}`);
      load();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  return (
    <div>
      <h1>Admin Panel</h1>
      {error && <div className="alert alert-error">{error}</div>}

      <div className="card">
        <h3>System Roles</h3>
        <div className="role-chip-list">
          {roles.map((r) => (
            <span key={r} className="role-chip">
              {r}
            </span>
          ))}
        </div>
      </div>

      <h2>All System Users</h2>
      <table className="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Admin</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id}>
              <td>{u.id}</td>
              <td>{u.name}</td>
              <td>{u.email}</td>
              <td>{u.role}</td>
              <td>{u.is_admin ? "Yes" : "No"}</td>
              <td>{u.is_active ? "Active" : "Inactive"}</td>
              <td>
                <button className="btn btn-small btn-secondary" onClick={() => toggleActive(u)}>
                  {u.is_active ? "Deactivate" : "Activate"}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
