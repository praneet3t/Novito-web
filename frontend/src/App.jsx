// frontend/src/App.jsx
import React, { useEffect, useState } from "react";

const API_BASE = ""; // If backend runs on different origin, set like "http://localhost:8000"

function useAuth() {
  const [token, setToken] = useState(() => localStorage.getItem("ma_token") || "");
  const [username, setUsername] = useState(() => localStorage.getItem("ma_username") || "");
  const [isAdmin, setIsAdmin] = useState(() => {
    const val = localStorage.getItem("ma_is_admin");
    return val === "true";
  });

  useEffect(() => {
    if (token) localStorage.setItem("ma_token", token);
    else localStorage.removeItem("ma_token");
  }, [token]);

  useEffect(() => {
    if (username) localStorage.setItem("ma_username", username);
    else localStorage.removeItem("ma_username");
  }, [username]);

  useEffect(() => {
    localStorage.setItem("ma_is_admin", isAdmin ? "true" : "false");
  }, [isAdmin]);

  const logout = () => {
    setToken("");
    setUsername("");
    setIsAdmin(false);
    localStorage.removeItem("ma_token");
    localStorage.removeItem("ma_username");
    localStorage.removeItem("ma_is_admin");
  };

  return { token, setToken, username, setUsername, isAdmin, setIsAdmin, logout };
}

async function apiFetch(path, token, opts = {}) {
  const headers = opts.headers ? { ...opts.headers } : {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(API_BASE + path, { ...opts, headers });
  if (res.status === 401) throw new Error("Unauthorized");
  return res;
}

export default function App() {
  const auth = useAuth();
  const { token, setToken, username, setUsername, isAdmin, setIsAdmin, logout } = auth;

  const [view, setView] = useState("login");

  useEffect(() => {
    if (token) determineRole();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  async function determineRole() {
    try {
      const res = await apiFetch("/meetings", token, { method: "GET" });
      if (res.ok) setIsAdmin(true);
      else setIsAdmin(false);
    } catch (e) {
      setIsAdmin(false);
    }
  }

  return (
    <div className="app-root">
      <header className="topbar">
        <h1 className="brand">Meeting Agent</h1>
        <div className="header-right">
          {token ? (
            <>
              <div className="who">
                {username}
                {isAdmin ? " (Admin)" : ""}
              </div>
              <button className="btn small" onClick={() => { logout(); setView("login"); }}>
                Logout
              </button>
            </>
          ) : null}
        </div>
      </header>

      <main className="container">
        {!token && (
          <AuthForms
            setToken={setToken}
            setUsername={setUsername}
            setView={setView}
            setIsAdmin={setIsAdmin}
          />
        )}
        {token && isAdmin && <AdminDashboard token={token} />}
        {token && !isAdmin && <UserDashboard token={token} />}
      </main>

      <footer className="footer">Built with ❤️ — Meeting Agent</footer>
    </div>
  );
}

function AuthForms({ setToken, setUsername, setView, setIsAdmin }) {
  const [loginUser, setLoginUser] = useState("");
  const [loginPass, setLoginPass] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleLogin(e) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: loginUser, password: loginPass }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Login failed");
      }
      const data = await res.json();
      setToken(data.access_token);
      setUsername(loginUser);

      try {
        const m = await fetch("/meetings", { headers: { Authorization: `Bearer ${data.access_token}` } });
        setIsAdmin(m.ok);
      } catch (e) {
        setIsAdmin(false);
      }

      setView("dashboard");
    } catch (err) {
      setError(err.message || "Login error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card auth-card">
      <h2>Sign in</h2>
      <form onSubmit={handleLogin} className="stack">
        <label>
          <div className="label-text">Username</div>
          <input value={loginUser} onChange={(e) => setLoginUser(e.target.value)} required />
        </label>
        <label>
          <div className="label-text">Password</div>
          <input type="password" value={loginPass} onChange={(e) => setLoginPass(e.target.value)} required />
        </label>
        <div className="actions">
          <button className="btn" type="submit" disabled={loading}>
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </div>
        {error && <div className="error">{error}</div>}
      </form>
      <p className="muted small">
        Seeded demo users: <strong>Priya</strong>, <strong>Arjun</strong>, <strong>Raghav</strong> (use seeded passwords) or <strong>Admin/admin123</strong>
      </p>
    </div>
  );
}

// ---------------- Admin Dashboard ----------------
function AdminDashboard({ token }) {
  return (
    <div className="grid two-col">
      <div className="col">
        <ProcessMeeting token={token} />
        <ManualTask token={token} />
      </div>
      <div className="col">
        <MeetingsList token={token} />
        <AllTasks token={token} />
      </div>
    </div>
  );
}

function ProcessMeeting({ token }) {
  const [title, setTitle] = useState("");
  const [date, setDate] = useState("");
  const [transcript, setTranscript] = useState("");
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setStatus("Processing...");
    try {
      const fd = new FormData();
      fd.append("title", title);
      if (date) fd.append("date", date);
      if (transcript) fd.append("transcript", transcript);
      if (file) fd.append("file", file);

      const res = await fetch("/meetings/process", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: fd,
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || "Processing failed");
      }
      const mt = await res.json();
      setStatus("Meeting processed: " + (mt.title || ""));
      setTitle("");
      setTranscript("");
      setFile(null);
      setDate("");
      window.dispatchEvent(new Event("ma_refresh"));
    } catch (err) {
      setStatus(err.message || "Error");
    }
  }

  return (
    <div className="card">
      <h3>Process Meeting</h3>
      <form onSubmit={handleSubmit} className="stack">
        <label>
          <div className="label-text">Title</div>
          <input value={title} onChange={(e) => setTitle(e.target.value)} required />
        </label>
        <label>
          <div className="label-text">Date (ISO)</div>
          <input value={date} onChange={(e) => setDate(e.target.value)} placeholder="2025-10-03T12:00:00" />
        </label>
        <label>
          <div className="label-text">Transcript (paste raw text)</div>
          <textarea value={transcript} onChange={(e) => setTranscript(e.target.value)} rows={6} />
        </label>
        <label>
          <div className="label-text">Or upload audio file</div>
          <input type="file" accept="audio/*" onChange={(e) => setFile(e.target.files[0])} />
        </label>
        <div className="actions">
          <button className="btn" type="submit">Process</button>
        </div>
        {status && <div className="muted">{status}</div>}
      </form>
    </div>
  );
}

function ManualTask({ token }) {
  const [desc, setDesc] = useState("");
  const [meetingId, setMeetingId] = useState("");
  const [assignee, setAssignee] = useState("");
  const [due, setDue] = useState("");
  const [status, setStatus] = useState("");

  async function handleCreate(e) {
    e.preventDefault();
    setStatus("Creating...");
    try {
      const res = await fetch("/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ description: desc, meeting_id: Number(meetingId), assignee_username: assignee, due_date: due || null }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Failed");
      }
      const t = await res.json();
      setStatus("Task created: " + t.id);
      setDesc("");
      setMeetingId("");
      setAssignee("");
      setDue("");
      window.dispatchEvent(new Event("ma_refresh"));
    } catch (err) {
      setStatus(err.message || "Error");
    }
  }

  return (
    <div className="card">
      <h3>Create Task (Admin)</h3>
      <form onSubmit={handleCreate} className="stack">
        <label>
          <div className="label-text">Description</div>
          <input value={desc} onChange={(e) => setDesc(e.target.value)} required />
        </label>
        <label>
          <div className="label-text">Meeting ID</div>
          <input value={meetingId} onChange={(e) => setMeetingId(e.target.value)} required />
        </label>
        <label>
          <div className="label-text">Assignee username</div>
          <input value={assignee} onChange={(e) => setAssignee(e.target.value)} required />
        </label>
        <label>
          <div className="label-text">Due date (optional ISO)</div>
          <input value={due} onChange={(e) => setDue(e.target.value)} />
        </label>
        <div className="actions">
          <button className="btn" type="submit">Create</button>
        </div>
        {status && <div className="muted">{status}</div>}
      </form>
    </div>
  );
}

function MeetingsList({ token }) {
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const res = await fetch("/meetings", { headers: { Authorization: `Bearer ${token}` } });
      if (!res.ok) throw new Error("Failed to load");
      const data = await res.json();
      setMeetings(data);
    } catch (e) {
      setMeetings([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    const h = () => load();
    window.addEventListener("ma_refresh", h);
    return () => window.removeEventListener("ma_refresh", h);
  }, [token]);

  return (
    <div className="card">
      <h3>Meetings</h3>
      {loading ? <div className="muted">Loading...</div> : (
        <div className="list">
          {meetings.length === 0 && <div className="muted">No meetings yet.</div>}
          {meetings.map(m => (
            <div key={m.id} className="item">
              <div className="item-head">
                <strong>{m.title}</strong>
                <div className="muted small">{m.date}</div>
              </div>
              {m.summary_minutes && <p className="summary">{m.summary_minutes}</p>}
              <div className="meta">Meeting ID: {m.id} • Processed by: {m.processed_by_id || "N/A"}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function AllTasks({ token }) {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const res = await fetch("/tasks", { headers: { Authorization: `Bearer ${token}` } });
      if (!res.ok) throw new Error("Failed");
      const data = await res.json();
      setTasks(data);
    } catch (e) {
      setTasks([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    const h = () => load();
    window.addEventListener("ma_refresh", h);
    return () => window.removeEventListener("ma_refresh", h);
  }, [token]);

  return (
    <div className="card">
      <h3>All Tasks</h3>
      {loading ? <div className="muted">Loading...</div> : (
        <div className="list">
          {tasks.length === 0 && <div className="muted">No tasks.</div>}
          {tasks.map(t => (
            <div key={t.id} className="item">
              <div className="row">
                <div><strong>{t.description}</strong></div>
                <div className="muted">Status: {t.status}</div>
              </div>
              <div className="muted small">Meeting: {t.meeting_id} • Assignee: {t.assignee_id}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ---------------- User Dashboard ----------------
function UserDashboard({ token }) {
  return (
    <div className="grid single">
      <MyTasks token={token} />
    </div>
  );
}

function MyTasks({ token }) {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const res = await fetch("/tasks/my", { headers: { Authorization: `Bearer ${token}` } });
      if (!res.ok) throw new Error("Failed");
      const data = await res.json();
      setTasks(data);
    } catch (e) {
      setTasks([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    const h = () => load();
    window.addEventListener("ma_refresh", h);
    return () => window.removeEventListener("ma_refresh", h);
  }, [token]);

  async function markDone(id) {
    try {
      const res = await fetch(`/tasks/${id}/complete`, { method: "POST", headers: { Authorization: `Bearer ${token}` } });
      if (!res.ok) throw new Error("Failed");
      window.dispatchEvent(new Event("ma_refresh"));
    } catch (e) {
      alert("Could not mark complete: " + e.message);
    }
  }

  return (
    <div className="card">
      <h3>My Tasks</h3>
      {loading ? <div className="muted">Loading...</div> : (
        <div className="list">
          {tasks.length === 0 && <div className="muted">No tasks assigned to you.</div>}
          {tasks.map(t => (
            <div key={t.id} className="item">
              <div className="row">
                <div><strong>{t.description}</strong></div>
                <div className="muted">{t.due_date || "No due date"}</div>
              </div>
              <div className="meta">Meeting: {t.meeting_id}</div>
              <div className="actions">
                {t.status !== "Done" ? <button className="btn small" onClick={() => markDone(t.id)}>Mark Done</button> : <span className="muted">Completed</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
