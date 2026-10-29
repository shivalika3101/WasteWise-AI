import { useEffect, useState } from "react";

import { useAuth } from "../context/useAuth";
import {
  createAdminBin,
  deactivateAdminBin,
  deleteAdminBin,
  fetchAdminBins,
  reactivateAdminBin,
  updateAdminBin,
} from "../services/api";

const EMPTY_FORM = { name: "", colour: "", description: "" };

function AdminBins() {
  const { token } = useAuth();
  const [bins, setBins] = useState([]);
  const [status, setStatus] = useState("loading");
  const [actionError, setActionError] = useState("");
  const [pendingId, setPendingId] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [editingId, setEditingId] = useState(null);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    let isCurrent = true;

    fetchAdminBins(token)
      .then((result) => {
        if (isCurrent) {
          setBins(result);
          setStatus("ready");
        }
      })
      .catch((error) => {
        if (isCurrent) {
          setStatus(error.status === 401 ? "expired" : "error");
        }
      });

    return () => {
      isCurrent = false;
    };
  }, [token]);

  function startEdit(bin) {
    setEditingId(bin.id);
    setForm({ name: bin.name, colour: bin.colour ?? "", description: bin.description ?? "" });
    setActionError("");
  }

  function cancelEdit() {
    setEditingId(null);
    setForm(EMPTY_FORM);
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setActionError("");
    setIsSaving(true);

    const payload = {
      name: form.name,
      colour: form.colour || null,
      description: form.description || null,
    };

    try {
      if (editingId) {
        const updated = await updateAdminBin(token, editingId, payload);
        setBins((current) => current.map((bin) => (bin.id === updated.id ? updated : bin)));
      } else {
        const created = await createAdminBin(token, payload);
        setBins((current) => [...current, created]);
      }
      cancelEdit();
    } catch (error) {
      setActionError(error.message);
    } finally {
      setIsSaving(false);
    }
  }

  async function toggleActive(bin) {
    const verb = bin.is_active ? "deactivate" : "reactivate";
    if (!window.confirm(`Are you sure you want to ${verb} ${bin.name}?`)) {
      return;
    }

    setActionError("");
    setPendingId(bin.id);

    try {
      const updated = bin.is_active
        ? await deactivateAdminBin(token, bin.id)
        : await reactivateAdminBin(token, bin.id);
      setBins((current) => current.map((existing) => (existing.id === updated.id ? updated : existing)));
    } catch (error) {
      setActionError(error.message);
    } finally {
      setPendingId(null);
    }
  }

  async function removeBin(bin) {
    if (!window.confirm(`Permanently delete ${bin.name}? This cannot be undone.`)) {
      return;
    }

    setActionError("");
    setPendingId(bin.id);

    try {
      await deleteAdminBin(token, bin.id);
      setBins((current) => current.filter((existing) => existing.id !== bin.id));
    } catch (error) {
      setActionError(error.message);
    } finally {
      setPendingId(null);
    }
  }

  if (status === "loading") {
    return <p className="history-status">Loading bins...</p>;
  }

  if (status === "expired") {
    return <p className="form-message error">Your sign-in session has expired. Please sign in again.</p>;
  }

  if (status === "error") {
    return <p className="form-message error">Could not load bins. Please try again later.</p>;
  }

  return (
    <>
      <section className="card-surface">
        <h2>{editingId ? "Update bin" : "Create bin"}</h2>
        <form className="auth-form" onSubmit={handleSubmit}>
          <label>
            Name
            <input
              value={form.name}
              onChange={(event) => setForm({ ...form, name: event.target.value })}
              required
            />
          </label>
          <label>
            Colour
            <input
              value={form.colour}
              onChange={(event) => setForm({ ...form, colour: event.target.value })}
            />
          </label>
          <label>
            Description
            <input
              value={form.description}
              onChange={(event) => setForm({ ...form, description: event.target.value })}
            />
          </label>
          <div className="button-group">
            <button className="primary-button" type="submit" disabled={isSaving}>
              {isSaving ? "Saving..." : editingId ? "Update bin" : "Create bin"}
            </button>
            {editingId ? (
              <button className="ghost-button" type="button" onClick={cancelEdit}>
                Cancel
              </button>
            ) : null}
          </div>
        </form>
      </section>

      {actionError ? <p className="form-message error">{actionError}</p> : null}

      <section className="card-surface">
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Colour</th>
                <th>Description</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {bins.map((bin) => (
                <tr key={bin.id}>
                  <td>{bin.name}</td>
                  <td>{bin.colour ?? "-"}</td>
                  <td>{bin.description ?? "-"}</td>
                  <td>{bin.is_active ? "Active" : "Deactivated"}</td>
                  <td className="admin-actions">
                    <button className="ghost-button" type="button" onClick={() => startEdit(bin)}>
                      Edit
                    </button>
                    <button
                      className="ghost-button"
                      type="button"
                      disabled={pendingId === bin.id}
                      onClick={() => toggleActive(bin)}
                    >
                      {bin.is_active ? "Deactivate" : "Reactivate"}
                    </button>
                    <button
                      className="ghost-button"
                      type="button"
                      disabled={pendingId === bin.id}
                      onClick={() => removeBin(bin)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}

export default AdminBins;
