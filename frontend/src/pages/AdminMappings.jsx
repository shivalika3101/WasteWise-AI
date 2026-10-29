import { useEffect, useState } from "react";

import { useAuth } from "../context/useAuth";
import {
  createAdminCategoryBin,
  deleteAdminCategoryBin,
  fetchAdminBins,
  fetchAdminCategories,
  fetchAdminCategoryBins,
  updateAdminCategoryBin,
} from "../services/api";

const EMPTY_FORM = { category_id: "", bin_id: "", is_primary: false };

function AdminMappings() {
  const { token } = useAuth();
  const [categories, setCategories] = useState([]);
  const [bins, setBins] = useState([]);
  const [mappings, setMappings] = useState([]);
  const [status, setStatus] = useState("loading");
  const [actionError, setActionError] = useState("");
  const [pendingId, setPendingId] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    let isCurrent = true;

    Promise.all([fetchAdminCategories(token), fetchAdminBins(token), fetchAdminCategoryBins(token)])
      .then(([categoriesResult, binsResult, mappingsResult]) => {
        if (isCurrent) {
          setCategories(categoriesResult);
          setBins(binsResult);
          setMappings(mappingsResult);
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

  function binName(binId) {
    const bin = bins.find((existing) => existing.id === binId);
    return bin ? bin.name : `#${binId}`;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setActionError("");
    setIsSaving(true);

    try {
      const created = await createAdminCategoryBin(token, {
        category_id: Number(form.category_id),
        bin_id: Number(form.bin_id),
        is_primary: form.is_primary,
      });
      setMappings((current) => [...current, created]);
      setForm(EMPTY_FORM);
    } catch (error) {
      setActionError(error.message);
    } finally {
      setIsSaving(false);
    }
  }

  async function togglePrimary(mapping) {
    const verb = mapping.is_primary ? "unset" : "set";
    if (!window.confirm(`Are you sure you want to ${verb} this mapping as primary?`)) {
      return;
    }

    setActionError("");
    setPendingId(mapping.id);

    try {
      const updated = await updateAdminCategoryBin(token, mapping.id, { is_primary: !mapping.is_primary });
      setMappings((current) => current.map((existing) => (existing.id === updated.id ? updated : existing)));
    } catch (error) {
      setActionError(error.message);
    } finally {
      setPendingId(null);
    }
  }

  async function removeMapping(mapping) {
    if (!window.confirm("Disconnect this category from this bin?")) {
      return;
    }

    setActionError("");
    setPendingId(mapping.id);

    try {
      await deleteAdminCategoryBin(token, mapping.id);
      setMappings((current) => current.filter((existing) => existing.id !== mapping.id));
    } catch (error) {
      setActionError(error.message);
    } finally {
      setPendingId(null);
    }
  }

  if (status === "loading") {
    return <p className="history-status">Loading mappings...</p>;
  }

  if (status === "expired") {
    return <p className="form-message error">Your sign-in session has expired. Please sign in again.</p>;
  }

  if (status === "error") {
    return <p className="form-message error">Could not load mappings. Please try again later.</p>;
  }

  return (
    <>
      <section className="card-surface">
        <h2>Connect a category to a bin</h2>
        <form className="auth-form" onSubmit={handleSubmit}>
          <label>
            Category
            <select
              value={form.category_id}
              onChange={(event) => setForm({ ...form, category_id: event.target.value })}
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
            Bin
            <select
              value={form.bin_id}
              onChange={(event) => setForm({ ...form, bin_id: event.target.value })}
              required
            >
              <option value="" disabled>
                Select a bin
              </option>
              {bins.map((bin) => (
                <option key={bin.id} value={bin.id}>
                  {bin.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            <input
              type="checkbox"
              checked={form.is_primary}
              onChange={(event) => setForm({ ...form, is_primary: event.target.checked })}
            />{" "}
            Primary bin for this category
          </label>
          <button className="primary-button" type="submit" disabled={isSaving}>
            {isSaving ? "Connecting..." : "Connect"}
          </button>
        </form>
      </section>

      {actionError ? <p className="form-message error">{actionError}</p> : null}

      <section className="card-surface">
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Category</th>
                <th>Bin</th>
                <th>Primary</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {mappings.map((mapping) => (
                <tr key={mapping.id}>
                  <td>{categoryName(mapping.category_id)}</td>
                  <td>{binName(mapping.bin_id)}</td>
                  <td>{mapping.is_primary ? "Yes" : "No"}</td>
                  <td className="admin-actions">
                    <button
                      className="ghost-button"
                      type="button"
                      disabled={pendingId === mapping.id}
                      onClick={() => togglePrimary(mapping)}
                    >
                      {mapping.is_primary ? "Unset primary" : "Set primary"}
                    </button>
                    <button
                      className="ghost-button"
                      type="button"
                      disabled={pendingId === mapping.id}
                      onClick={() => removeMapping(mapping)}
                    >
                      Disconnect
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

export default AdminMappings;
