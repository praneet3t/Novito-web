import { useState, useEffect } from "react";
import { api } from "../utils/api";

export default function CaptureInbox({ token }) {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const data = await api.tasks.list(token);
      setTasks(data.filter(t => t.status === "Capture Inbox"));
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

  async function moveToReview(id) {
    try {
      await api.tasks.update(token, id, { status: "To Do", is_approved: false });
      window.dispatchEvent(new Event("ma_refresh"));
    } catch (e) {
      alert("Failed: " + e.message);
    }
  }

  return (
    <div className="card">
      <h3>Capture Inbox</h3>
      <p className="muted small">Quick captured tasks awaiting planning</p>
      {loading ? (
        <div className="loading-spinner"></div>
      ) : (
        <div className="list">
          {tasks.length === 0 && <div className="muted">No captured tasks</div>}
          {tasks.map(t => (
            <div key={t.id} className="item">
              <strong>{t.description}</strong>
              <div className="actions">
                <button className="btn small" onClick={() => moveToReview(t.id)}>Move to Review</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
