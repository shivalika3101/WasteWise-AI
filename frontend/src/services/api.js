const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

async function request(path, options = {}) {
  const headers = new Headers(options.headers ?? {});
  const isFormData = options.body instanceof FormData;

  if (!isFormData && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  let response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers,
    });
  } catch {
    throw new Error(
      "Cannot reach the WasteWise API. Start the backend server, then try again.",
    );
  }

  if (response.status === 204) {
    return null;
  }

  const contentType = response.headers.get("content-type") ?? "";
  const body = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const detail =
      typeof body === "object" && body !== null && "detail" in body
        ? body.detail
        : "Something went wrong. Please try again.";
    const error = new Error(detail);
    error.status = response.status;
    throw error;
  }

  return body;
}

export function registerUser(payload) {
  return request("/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function loginUser(payload) {
  return request("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function logoutUser(token) {
  return request("/auth/logout", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export function fetchCurrentUser(token) {
  return request("/users/me", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export function createPrediction({ token, file }) {
  const body = new FormData();
  body.append("image", file);

  return request("/predictions/", {
    method: "POST",
    body,
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export function fetchPredictionHistory(token, { limit = 10, offset = 0 } = {}) {
  const query = new URLSearchParams({ limit: String(limit), offset: String(offset) });

  return request(`/predictions/history?${query}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export function fetchProfileSummary(token) {
  return request("/predictions/summary", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export function fetchBinOptions(token) {
  return request("/predictions/bins", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export function submitBinExamination({ token, predictionId, selectedBinId }) {
  return request(`/predictions/${predictionId}/bin-examinations`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ selected_bin_id: selectedBinId }),
  });
}


export function fetchBlogPosts() {
  return request("/blog/posts");
}

export function fetchBlogPost(slug) {
  return request(`/blog/posts/${encodeURIComponent(slug)}`);
}

export function fetchAdminUsers(token) {
  return request("/admin/users", {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function fetchAdminUser(token, userId) {
  return request(`/admin/users/${userId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function fetchAdminUserPredictions(token, userId, { limit = 20, offset = 0 } = {}) {
  const query = new URLSearchParams({ limit: String(limit), offset: String(offset) });

  return request(`/admin/users/${userId}/predictions?${query}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function deactivateAdminUser(token, userId) {
  return request(`/admin/users/${userId}/deactivate`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function reactivateAdminUser(token, userId) {
  return request(`/admin/users/${userId}/reactivate`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function fetchAdminBins(token) {
  return request("/admin/bins", {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function createAdminBin(token, payload) {
  return request("/admin/bins", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(payload),
  });
}

export function updateAdminBin(token, binId, payload) {
  return request(`/admin/bins/${binId}`, {
    method: "PATCH",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(payload),
  });
}

export function deactivateAdminBin(token, binId) {
  return request(`/admin/bins/${binId}/deactivate`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function reactivateAdminBin(token, binId) {
  return request(`/admin/bins/${binId}/reactivate`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function deleteAdminBin(token, binId) {
  return request(`/admin/bins/${binId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function fetchAdminDisposalInstructions(token) {
  return request("/admin/disposal-instructions", {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function createAdminDisposalInstruction(token, payload) {
  return request("/admin/disposal-instructions", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(payload),
  });
}

export function updateAdminDisposalInstruction(token, instructionId, payload) {
  return request(`/admin/disposal-instructions/${instructionId}`, {
    method: "PATCH",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(payload),
  });
}

export function deactivateAdminDisposalInstruction(token, instructionId) {
  return request(`/admin/disposal-instructions/${instructionId}/deactivate`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function reactivateAdminDisposalInstruction(token, instructionId) {
  return request(`/admin/disposal-instructions/${instructionId}/reactivate`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function fetchAdminCategories(token) {
  return request("/admin/categories", {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function fetchAdminCategoryBins(token) {
  return request("/admin/category-bins", {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function createAdminCategoryBin(token, payload) {
  return request("/admin/category-bins", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(payload),
  });
}

export function updateAdminCategoryBin(token, mappingId, payload) {
  return request(`/admin/category-bins/${mappingId}`, {
    method: "PATCH",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(payload),
  });
}

export function deleteAdminCategoryBin(token, mappingId) {
  return request(`/admin/category-bins/${mappingId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
}
