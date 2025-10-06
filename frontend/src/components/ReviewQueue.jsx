import { useState, useEffect } from "react";
import { api } from "../utils/api";

export default function ReviewQueue({ token }) {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const data = await api.tasks.review(token);
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

  async function approve(id) {
    try {
      await api.tasks.update(token, id, { is_approved: true });
      window.dispatchEvent(new Event("ma_refresh"));
    } catch (e) {
      alert("Failed: " + e.message);
    }
  }

  async function updatePriority(id, priority) {
    try {
      await api.tasks.update(token, id, { priority: Number(priority) });
      window.dispatchEvent(new Event("ma_refresh"));
    } catch (e) {
      alert("Failed: " + e.message);
    }
  }

  async function updateEffort(id, effort) {
    try {
      await api.tasks.update(token, id, { effort_tag: effort });
      window.dispatchEvent(new Event("ma_refresh"));
    } catch (e) {
      alert("Failed: " + e.message);
    }
  }

  return (
    <div className="card">
      <h3>Review Queue (Unapproved Tasks)</h3>
      {loading ? (
        <div className="muted">Loading...</div>
      ) : (
        <div className="list">
          {tasks.length === 0 && <div className="muted">No tasks to review</div>}
          {tasks.map((t) => (
            <div className="item" key={t.id}>
              <div className="row">
                <strong>{t.description}</strong>
                <div className="muted">Confidence: {(t.confidence * 100).toFixed(0)}%</div>
              </div>
              <div className="row">
                <label className="inline">
                  Priority:
                  <input
                    type="number"
                    defaultValue={t.priority}
                    onBlur={(e) => updatePriority(t.id, e.target.value)}
                    style={{ width: "60px", marginLeft: "8px" }}
                  />
                </label>
                <label className="inline">
                  Effort:
                  <select
                    defaultValue={t.effort_tag || ""}
                    onChange={(e) => updateEffort(t.id, e.target.value)}
                    style={{ marginLeft: "8px" }}
                  >
                    <option value="">None</option>
                    <option value="small">Small</option>
                    <option value="medium">Medium</option>
                    <option value="large">Large</option>
                  </select>
                </label>
              </div>
              <div className="actions">
                <button className="btn small" onClick={() => approve(t.id)}>Approve</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
