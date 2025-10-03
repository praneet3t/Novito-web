// frontend/src/App.jsx
import React, { useEffect, useState } from "react";

const API_BASE = "http://127.0.0.1:8000"; // backend URL - adjust if different

function useAuth() {
  const [token, setToken] = useState(() => localStorage.getItem("ma_token") || "");
  const [username, setUsername] = useState(() => localStorage.getItem("ma_username") || "");
  const [isAdmin, setIsAdmin] = useState(() => localStorage.getItem("ma_is_admin") === "true");

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

export default function App() {
  const { token, setToken, username, setUsername, isAdmin, setIsAdmin, logout } = useAuth();
  const [view, setView] = useState("login");

  useEffect(() => {
    // if token exists, keep view as dashboard
    if (token) setView("dashboard");
  }, [token]);

  return (
    <div className="app-root">
      <header className="topbar">
        <h1 className="brand">Meeting Agent (Demo)</h1>
        <div className="header-right">
          {token ? (
            <>
              <div className="who">{username} {isAdmin ? "(Admin)" : ""}</div>
              <button className="btn small" onClick={() => { logout(); setView("login"); }}>Logout</button>
            </>
          ) : null}
        </div>
      </header>

      <main className="container">
        {!token && <AuthForms setToken={setToken} setUsername={setUsername} setIsAdmin={setIsAdmin} />}
        {token && isAdmin && <AdminDashboard token={token} />}
        {token && !isAdmin && <UserDashboard token={token} />}
      </main>

      <footer className="footer">Demo — Meeting Agent</footer>
    </div>
  );
}

function AuthForms({ setToken, setUsername, setIsAdmin }) {
  const [user, setUser] = useState("");
  const [pass, setPass] = useState("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  async function handleLogin(e) {
    e.preventDefault();
    setLoading(true);
    setErr("");
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: user, password: pass }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || "Login failed");
      }
      const data = await res.json();
      setToken(data.token);
      setUsername(data.username);
      setIsAdmin(!!data.is_admin);
    } catch (e) {
      setErr(e.message || "Login error");
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
          <input value={user} onChange={(e) => setUser(e.target.value)} required />
        </label>
        <label>
          <div className="label-text">Password</div>
          <input type="password" value={pass} onChange={(e) => setPass(e.target.value)} required />
        </label>
        <div className="actions">
          <button className="btn" type="submit" disabled={loading}>{loading ? "Signing in..." : "Sign in"}</button>
        </div>
        {err && <div className="error">{err}</div>}
      </form>
      <p className="muted small">Demo accounts: Priya/priya123, Arjun/arjun456, Raghav/raghav789, Admin/admin123</p>
    </div>
  );
}

/* ---------- Admin UI ---------- */
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

      const res = await fetch(`${API_BASE}/meetings/process`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` },
        body: fd,
      });
      if (!res.ok) {
        const b = await res.json().catch(() => ({}));
        throw new Error(b.detail || "Failed");
      }
      const mt = await res.json();
      setStatus("Processed: " + mt.title);
      setTitle(""); setTranscript(""); setFile(null); setDate("");
      window.dispatchEvent(new Event("ma_refresh"));
    } catch (e) {
      setStatus(e.message || "Error");
    }
  }

  return (
    <div className="card">
      <h3>Process Meeting</h3>
      <form onSubmit={handleSubmit} className="stack">
        <label><div className="label-text">Title</div><input value={title} onChange={(e) => setTitle(e.target.value)} required /></label>
        <label><div className="label-text">Date (ISO)</div><input value={date} onChange={(e) => setDate(e.target.value)} /></label>
        <label><div className="label-text">Transcript</div><textarea value={transcript} onChange={(e) => setTranscript(e.target.value)} rows={6}></textarea></label>
        <label><div className="label-text">Upload audio (optional)</div><input type="file" accept="audio/*" onChange={(e) => setFile(e.target.files[0])} /></label>
        <div className="actions"><button className="btn" type="submit">Process</button></div>
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
      const res = await fetch(`${API_BASE}/tasks`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
        body: JSON.stringify({ description: desc, meeting_id: Number(meetingId), assignee_username: assignee, due_date: due || null }),
      });
      if (!res.ok) {
        const b = await res.json().catch(() => ({}));
        throw new Error(b.detail || "Failed");
      }
      const t = await res.json();
      setStatus("Task created: " + t.id);
      setDesc(""); setMeetingId(""); setAssignee(""); setDue("");
      window.dispatchEvent(new Event("ma_refresh"));
    } catch (e) {
      setStatus(e.message || "Error");
    }
  }

  return (
    <div className="card">
      <h3>Create Task</h3>
      <form onSubmit={handleCreate} className="stack">
        <label><div className="label-text">Description</div><input value={desc} onChange={(e) => setDesc(e.target.value)} required /></label>
        <label><div className="label-text">Meeting ID</div><input value={meetingId} onChange={(e) => setMeetingId(e.target.value)} required /></label>
        <label><div className="label-text">Assignee</div><input value={assignee} onChange={(e) => setAssignee(e.target.value)} required /></label>
        <label><div className="label-text">Due (optional)</div><input value={due} onChange={(e) => setDue(e.target.value)} /></label>
        <div className="actions"><button className="btn" type="submit">Create</button></div>
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
      const res = await fetch(`${API_BASE}/meetings`, { headers: { "Authorization": `Bearer ${token}` } });
      if (!res.ok) throw new Error("Failed");
      const data = await res.json();
      setMeetings(data);
    } catch (e) {
      setMeetings([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); const h = () => load(); window.addEventListener("ma_refresh", h); return () => window.removeEventListener("ma_refresh", h); }, [token]);

  return (
    <div className="card">
      <h3>Meetings</h3>
      {loading ? <div className="muted">Loading...</div> : (
        <div className="list">
          {meetings.length === 0 && <div className="muted">No meetings</div>}
          {meetings.map(m => (
            <div className="item" key={m.id}>
              <div className="item-head"><strong>{m.title}</strong><div className="muted small">{m.date}</div></div>
              {m.summary_minutes && <p className="summary">{m.summary_minutes}</p>}
              <div className="meta">ID: {m.id} • By: {m.processed_by_id || "N/A"}</div>
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
      const res = await fetch(`${API_BASE}/tasks`, { headers: { "Authorization": `Bearer ${token}` } });
      if (!res.ok) throw new Error("Failed");
      setTasks(await res.json());
    } catch (e) {
      setTasks([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); const h = () => load(); window.addEventListener("ma_refresh", h); return () => window.removeEventListener("ma_refresh", h); }, [token]);

  return (
    <div className="card">
      <h3>All Tasks</h3>
      {loading ? <div className="muted">Loading...</div> : (
        <div className="list">
          {tasks.length === 0 && <div className="muted">No tasks</div>}
          {tasks.map(t => (
            <div className="item" key={t.id}>
              <div className="row"><div><strong>{t.description}</strong></div><div className="muted">Status: {t.status}</div></div>
              <div className="muted small">Meeting: {t.meeting_id} • Assignee: {t.assignee_id}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ---------- User UI ---------- */

function UserDashboard({ token }) {
  return <div className="grid single"><MyTasks token={token} /></div>;
}

function MyTasks({ token }) {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/tasks/my`, { headers: { "Authorization": `Bearer ${token}` } });
      if (!res.ok) throw new Error("Failed");
      setTasks(await res.json());
    } catch (e) {
      setTasks([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); const h = () => load(); window.addEventListener("ma_refresh", h); return () => window.removeEventListener("ma_refresh", h); }, [token]);

  async function markDone(id) {
    try {
      const res = await fetch(`${API_BASE}/tasks/${id}/complete`, { method: "POST", headers: { "Authorization": `Bearer ${token}` } });
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
          {tasks.length === 0 && <div className="muted">No tasks assigned</div>}
          {tasks.map(t => (
            <div className="item" key={t.id}>
              <div className="row"><div><strong>{t.description}</strong></div><div className="muted">{t.due_date || "No due"}</div></div>
              <div className="meta">Meeting: {t.meeting_id}</div>
              <div className="actions">{t.status !== "Done" ? <button className="btn small" onClick={() => markDone(t.id)}>Mark Done</button> : <span className="muted">Completed</span>}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
