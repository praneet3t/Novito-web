import { useState, useEffect } from "react";
import { api } from "../utils/api";

export default function AllTasks({ token }) {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const data = await api.tasks.list(token);
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
      {loading ? (
        <div className="muted">Loading...</div>
      ) : (
        <div className="list">
          {tasks.length === 0 && <div className="muted">No tasks</div>}
          {tasks.map((t) => (
            <div className="item" key={t.id}>
              <div className="row">
                <div>
                  <strong>{t.description}</strong>
                </div>
                <div className="muted">Status: {t.status}</div>
              </div>
              <div className="muted small">
                Priority: {t.priority} • Effort: {t.effort_tag || "N/A"} • Approved: {t.is_approved ? "✓" : "✗"}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
