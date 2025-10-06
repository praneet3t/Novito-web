import { useState, useEffect } from "react";
import { api } from "../utils/api";

export default function PriorityQueue({ token }) {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const data = await api.tasks.queue(token);
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
      <h3>Priority Queue (Approved Tasks)</h3>
      {loading ? (
        <div className="muted">Loading...</div>
      ) : (
        <div className="list">
          {tasks.length === 0 && <div className="muted">No approved tasks in queue</div>}
          {tasks.map((t) => (
            <div className="item" key={t.id}>
              <div className="row">
                <div>
                  <span className="badge priority">P{t.priority}</span>
                  <strong style={{marginLeft: '8px'}}>{t.description}</strong>
                </div>
                <span className={`badge ${t.effort_tag || 'medium'}`}>{t.effort_tag || "?"}</span>
              </div>
              <div className="muted small">Status: {t.status} • Due: {t.due_date || 'No deadline'}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
