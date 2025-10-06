import { useState, useEffect } from "react";
import { api } from "../utils/api";

export default function MyTasks({ token }) {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const data = await api.tasks.my(token);
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
      await api.tasks.complete(token, id);
      window.dispatchEvent(new Event("ma_refresh"));
    } catch (e) {
      alert("Could not mark complete: " + e.message);
    }
  }

  return (
    <div className="card">
      <h3>My Tasks</h3>
      {loading ? (
        <div className="muted">Loading...</div>
      ) : (
        <div className="list">
          {tasks.length === 0 && <div className="muted">No tasks assigned</div>}
          {tasks.map((t) => (
            <div className="item" key={t.id}>
              <div className="row">
                <div>
                  <strong>{t.description}</strong>
                </div>
                <div className="muted">{t.due_date || "No due"}</div>
              </div>
              <div className="meta">
                Priority: {t.priority} • Effort: {t.effort_tag || "N/A"}
              </div>
              <div className="actions">
                {t.status !== "Done" ? (
                  <button className="btn small" onClick={() => markDone(t.id)}>Mark Done</button>
                ) : (
                  <span className="muted">Completed</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
