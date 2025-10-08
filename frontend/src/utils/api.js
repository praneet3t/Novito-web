export const API_BASE = "http://127.0.0.1:8000";

export const api = {
  async request(endpoint, options = {}) {
    const res = await fetch(`${API_BASE}${endpoint}`, options);
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.detail || "Request failed");
    }
    return res.json();
  },

  analytics: {
    briefing: (token) =>
      api.request("/analytics/briefing", {
        headers: { Authorization: `Bearer ${token}` },
      }),
    productivity: (token, days = 7) =>
      api.request(`/analytics/productivity?days=${days}`, {
        headers: { Authorization: `Bearer ${token}` },
      }),
  },

  auth: {
    login: (username, password) =>
      api.request("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      }),
  },

  meetings: {
    list: (token) =>
      api.request("/meetings", {
        headers: { Authorization: `Bearer ${token}` },
      }),
    process: (token, formData) =>
      api.request("/meetings/process", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      }),
  },

  tasks: {
    capture: (token, text) =>
      api.request("/tasks/capture", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ text }),
      }),
    planTomorrow: (token) =>
      api.request("/tasks/plan-tomorrow", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      }),
    submit: (token, id, data) =>
      api.request(`/tasks/${id}/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(data),
      }),
    verify: (token, id, data) =>
      api.request(`/tasks/${id}/verify`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(data),
      }),
    pendingVerification: (token) =>
      api.request("/tasks/pending-verification", {
        headers: { Authorization: `Bearer ${token}` },
      }),
    list: (token) =>
      api.request("/tasks", {
        headers: { Authorization: `Bearer ${token}` },
      }),
    my: (token) =>
      api.request("/tasks/my", {
        headers: { Authorization: `Bearer ${token}` },
      }),
    create: (token, data) =>
      api.request("/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(data),
      }),
    complete: (token, id) =>
      api.request(`/tasks/${id}/complete`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      }),
    update: (token, id, data) =>
      api.request(`/tasks/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(data),
      }),
    queue: (token) =>
      api.request("/tasks/queue", {
        headers: { Authorization: `Bearer ${token}` },
      }),
    review: (token) =>
      api.request("/tasks/review", {
        headers: { Authorization: `Bearer ${token}` },
      }),
  },

  workcycles: {
    list: (token) =>
      api.request("/workcycles", {
        headers: { Authorization: `Bearer ${token}` },
      }),
    create: (token, data) =>
      api.request("/workcycles", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(data),
      }),
    tasks: (token, id) =>
      api.request(`/workcycles/${id}/tasks`, {
        headers: { Authorization: `Bearer ${token}` },
      }),
    snapshot: (token, id) =>
      api.request(`/workcycles/${id}/snapshot`, {
        headers: { Authorization: `Bearer ${token}` },
      }),
  },

  notifications: {
    list: (token) =>
      api.request("/notifications", {
        headers: { Authorization: `Bearer ${token}` },
      }),
    markRead: (token, id) =>
      api.request(`/notifications/${id}/read`, {
        method: "PATCH",
        headers: { Authorization: `Bearer ${token}` },
      }),
  },

  bundles: {
    list: (token) =>
      api.request("/bundles", {
        headers: { Authorization: `Bearer ${token}` },
      }),
    create: (token, data) =>
      api.request("/bundles", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(data),
      }),
    tasks: (token, id) =>
      api.request(`/bundles/${id}/tasks`, {
        headers: { Authorization: `Bearer ${token}` },
      }),
  },
};
