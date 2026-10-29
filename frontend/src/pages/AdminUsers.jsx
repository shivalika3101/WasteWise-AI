import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { useAuth } from "../context/useAuth";
import {
  deactivateAdminUser,
  fetchAdminUsers,
  reactivateAdminUser,
} from "../services/api";

function AdminUsers() {
  const { signOut, token } = useAuth();
  const [users, setUsers] = useState([]);
  const [status, setStatus] = useState("loading");
  const [actionError, setActionError] = useState("");
  const [pendingUserId, setPendingUserId] = useState(null);

  useEffect(() => {
    let isCurrent = true;

    async function loadUsers() {
      try {
        const result = await fetchAdminUsers(token);
        if (isCurrent) {
          setUsers(result);
          setStatus("ready");
        }
      } catch (error) {
        if (isCurrent) {
          setStatus(error.status === 401 ? "expired" : "error");
        }
      }
    }

    loadUsers();
    return () => {
      isCurrent = false;
    };
  }, [token]);

  async function toggleActive(user) {
    const isDeactivating = user.is_active;
    const verb = isDeactivating ? "deactivate" : "reactivate";
    if (!window.confirm(`Are you sure you want to ${verb} ${user.email}?`)) {
      return;
    }

    setActionError("");
    setPendingUserId(user.id);

    try {
      const updated = isDeactivating
        ? await deactivateAdminUser(token, user.id)
        : await reactivateAdminUser(token, user.id);
      setUsers((currentUsers) =>
        currentUsers.map((existing) => (existing.id === updated.id ? updated : existing)),
      );
    } catch (error) {
      setActionError(error.message);
    } finally {
      setPendingUserId(null);
    }
  }

  if (status === "loading") {
    return <p className="history-status">Loading users...</p>;
  }

  if (status === "expired") {
    return (
      <div className="form-message error">
        <p>Your sign-in session has expired. Please sign in again.</p>
        <button className="ghost-button" type="button" onClick={signOut}>
          Go to sign in
        </button>
      </div>
    );
  }

  if (status === "error") {
    return <p className="form-message error">Could not load users. Please try again later.</p>;
  }

  return (
    <section className="card-surface">
      {actionError ? <p className="form-message error">{actionError}</p> : null}
      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Email</th>
              <th>Role</th>
              <th>Status</th>
              <th>Joined</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id}>
                <td>{user.email}</td>
                <td>{user.role}</td>
                <td>{user.is_active ? "Active" : "Deactivated"}</td>
                <td>{new Date(user.created_at).toLocaleDateString()}</td>
                <td className="admin-actions">
                  <Link className="ghost-button link-button" to={`/console/users/${user.id}/predictions`}>
                    Predictions
                  </Link>
                  <button
                    className="ghost-button"
                    type="button"
                    disabled={pendingUserId === user.id}
                    onClick={() => toggleActive(user)}
                  >
                    {user.is_active ? "Deactivate" : "Reactivate"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export default AdminUsers;
