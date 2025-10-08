import { useState, useEffect } from "react";
import { api } from "../utils/api";

export default function ManagerApproval({ token }) {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const data = await api.tasks.list(token);
      setTasks(data.filter(t => t.status === "Manager Approval Pending"));
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
      await api.tasks.approveManager(token, id);
      window.dispatchEvent(new Event("ma_refresh"));
    } catch (e) {
      alert("Failed: " + e.message);
    }
  }

  return (
    <div className="card">
      <h3>Manager Approval Queue</h3>
      <p className="muted small">Large tasks (Story Points &gt; 8 or Large effort) require manager approval</p>
      {loading ? (
        <div className="loading-spinner"></div>
      ) : (
        <div className="list">
          {tasks.length === 0 && <div className="muted">No tasks pending approval</div>}
          {tasks.map(t => (
            <div key={t.id} className="item">
              <div className="row">
                <div>
                  <strong>{t.description}</strong>
                  <div className="muted small" style={{marginTop: '4px'}}>
                    Story Points: {t.story_points} | Effort: {t.effort_tag} | Priority: {t.priority}
                  </div>
                </div>
                <span className="story-points">{t.story_points} SP</span>
              </div>
              {t.acceptance_criteria && (
                <div style={{marginTop: '8px', padding: '8px', background: 'var(--bg)', borderRadius: '4px'}}>
                  <strong style={{fontSize: '12px'}}>Acceptance Criteria:</strong>
                  <p style={{fontSize: '12px', marginTop: '4px'}}>{t.acceptance_criteria}</p>
                </div>
              )}
              <div className="actions">
                <button className="btn small success" onClick={() => approve(t.id)}>Approve</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
