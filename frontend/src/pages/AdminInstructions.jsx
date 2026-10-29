import { useEffect, useState } from "react";

import { useAuth } from "../context/useAuth";
import {
  createAdminDisposalInstruction,
  deactivateAdminDisposalInstruction,
  fetchAdminCategories,
  fetchAdminDisposalInstructions,
  reactivateAdminDisposalInstruction,
  updateAdminDisposalInstruction,
} from "../services/api";

const EMPTY_FORM = { category_id: "", instructions: "", notes: "" };

function AdminInstructions() {
  const { token } = useAuth();
  const [categories, setCategories] = useState([]);
  const [instructions, setInstructions] = useState([]);
  const [status, setStatus] = useState("loading");
  const [actionError, setActionError] = useState("");
  const [pendingId, setPendingId] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [editingId, setEditingId] = useState(null);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    let isCurrent = true;

    Promise.all([fetchAdminCategories(token), fetchAdminDisposalInstructions(token)])
      .then(([categoriesResult, instructionsResult]) => {
        if (isCurrent) {
          setCategories(categoriesResult);
          setInstructions(instructionsResult);
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

  function categoryName(categoryId) {
    const category = categories.find((existing) => existing.id === categoryId);
    return category ? category.display_name || category.name : `#${categoryId}`;
  }

  function startEdit(instruction) {
    setEditingId(instruction.id);
    setForm({
      category_id: String(instruction.category_id),
      instructions: instruction.instructions,
      notes: instruction.notes ?? "",
    });
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

    try {
      if (editingId) {
        const updated = await updateAdminDisposalInstruction(token, editingId, {
          instructions: form.instructions,
          notes: form.notes || null,
        });
        setInstructions((current) =>
          current.map((instruction) => (instruction.id === updated.id ? updated : instruction)),
        );
      } else {
        const created = await createAdminDisposalInstruction(token, {
          category_id: Number(form.category_id),
          instructions: form.instructions,
          notes: form.notes || null,
        });
        setInstructions((current) => [...current, created]);
      }
      cancelEdit();
    } catch (error) {
      setActionError(error.message);
    } finally {
      setIsSaving(false);
    }
  }

  async function toggleActive(instruction) {
    const verb = instruction.is_active ? "deactivate" : "reactivate";
    if (!window.confirm(`Are you sure you want to ${verb} this instruction?`)) {
      return;
    }

    setActionError("");
    setPendingId(instruction.id);

    try {
      const updated = instruction.is_active
        ? await deactivateAdminDisposalInstruction(token, instruction.id)
        : await reactivateAdminDisposalInstruction(token, instruction.id);
      setInstructions((current) =>
        current.map((existing) => (existing.id === updated.id ? updated : existing)),
      );
    } catch (error) {
      setActionError(error.message);
    } finally {
      setPendingId(null);
    }
  }

  if (status === "loading") {
    return <p className="history-status">Loading disposal instructions...</p>;
  }

  if (status === "expired") {
    return <p className="form-message error">Your sign-in session has expired. Please sign in again.</p>;
  }

  if (status === "error") {
    return <p className="form-message error">Could not load disposal instructions. Please try again later.</p>;
  }

  return (
    <>
      <section className="card-surface">
        <h2>{editingId ? "Update instruction" : "Create instruction"}</h2>
        <form className="auth-form" onSubmit={handleSubmit}>
          <label>
            Category
            <select
              value={form.category_id}
              onChange={(event) => setForm({ ...form, category_id: event.target.value })}
              disabled={Boolean(editingId)}
              required
            >
              <option value="" disabled>
                Select a category
              </option>
              {categories.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.display_name || category.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Instructions
            <input
              value={form.instructions}
              onChange={(event) => setForm({ ...form, instructions: event.target.value })}
              required
            />
          </label>
          <label>
            Notes
            <input
              value={form.notes}
              onChange={(event) => setForm({ ...form, notes: event.target.value })}
            />
          </label>
          <div className="button-group">
            <button className="primary-button" type="submit" disabled={isSaving}>
              {isSaving ? "Saving..." : editingId ? "Update instruction" : "Create instruction"}
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
                <th>Category</th>
                <th>Instructions</th>
                <th>Notes</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {instructions.map((instruction) => (
                <tr key={instruction.id}>
                  <td>{categoryName(instruction.category_id)}</td>
                  <td>{instruction.instructions}</td>
                  <td>{instruction.notes ?? "-"}</td>
                  <td>{instruction.is_active ? "Active" : "Deactivated"}</td>
                  <td className="admin-actions">
                    <button className="ghost-button" type="button" onClick={() => startEdit(instruction)}>
                      Edit
                    </button>
                    <button
                      className="ghost-button"
                      type="button"
                      disabled={pendingId === instruction.id}
                      onClick={() => toggleActive(instruction)}
                    >
                      {instruction.is_active ? "Deactivate" : "Reactivate"}
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

export default AdminInstructions;
