import { useState } from "react";
import { api } from "../utils/api";

export default function LoginPage({ setToken, setUsername, setIsAdmin }) {
  const [user, setUser] = useState("");
  const [pass, setPass] = useState("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  async function handleLogin(e) {
    e.preventDefault();
    setLoading(true);
    setErr("");
    try {
      const data = await api.auth.login(user, pass);
      setToken(data.token);
      setUsername(data.username);
      setIsAdmin(!!data.is_admin);
    } catch (e) {
      setErr(e.message);
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
          <button className="btn" type="submit" disabled={loading}>
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </div>
        {err && <div className="error">{err}</div>}
      </form>
      <p className="muted small">Demo: Priya/priya123, Arjun/arjun456, Raghav/raghav789, Admin/admin123</p>
    </div>
  );
}
