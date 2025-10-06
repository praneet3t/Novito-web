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

  const [selectedTask, setSelectedTask] = useState(null);
  const [progress, setProgress] = useState(0);
  const [isBlocked, setIsBlocked] = useState(false);
  const [blockerReason, setBlockerReason] = useState("");

  async function updateProgress(id, prog) {
    try {
      await api.tasks.update(token, id, { progress: prog });
      window.dispatchEvent(new Event("ma_refresh"));
    } catch (e) {
      alert("Failed: " + e.message);
    }
  }

  async function markBlocked(id) {
    try {
      await api.tasks.update(token, id, { is_blocked: true, blocker_reason: blockerReason });
      setSelectedTask(null);
      setBlockerReason("");
      window.dispatchEvent(new Event("ma_refresh"));
    } catch (e) {
      alert("Failed: " + e.message);
    }
  }

  function getDeadlineStatus(dueDate) {
    if (!dueDate) return null;
    const today = new Date();
    const due = new Date(dueDate);
    const diff = Math.ceil((due - today) / (1000 * 60 * 60 * 24));
    
    if (diff < 0) return { class: 'overdue', text: `${Math.abs(diff)}d overdue`, icon: '🔴' };
    if (diff === 0) return { class: 'today', text: 'Due today', icon: '⚠️' };
    if (diff <= 3) return { class: 'upcoming', text: `${diff}d left`, icon: '⏰' };
    return { class: 'upcoming', text: `${diff}d left`, icon: '📅' };
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
                  {t.is_blocked && <span className="badge status-blocked" style={{marginLeft: '8px'}}>🚫 Blocked</span>}
                </div>
                {t.due_date && (() => {
                  const status = getDeadlineStatus(t.due_date);
                  return status ? <span className={`deadline-indicator ${status.class}`}>{status.icon} {status.text}</span> : null;
                })()}
              </div>
              
              <div className="row">
                <div className="meta">
                  Priority: {t.priority} • Status: {t.status}
                </div>
                {t.effort_tag && <span className={`badge ${t.effort_tag}`}>{t.effort_tag}</span>}
              </div>

              {t.is_blocked && t.blocker_reason && (
                <div className="alert danger" style={{marginTop: '8px', padding: '8px'}}>
                  <span>🚫</span>
                  <span>{t.blocker_reason}</span>
                </div>
              )}

              {t.status !== "Done" && !t.is_blocked && (
                <div style={{marginTop: '12px'}}>
                  <div className="muted small">Progress: {t.progress}%</div>
                  <div className="progress-bar">
                    <div className="progress-fill" style={{width: `${t.progress}%`}}></div>
                  </div>
                  <input 
                    type="range" 
                    min="0" 
                    max="100" 
                    value={t.progress} 
                    onChange={(e) => updateProgress(t.id, Number(e.target.value))}
                    style={{width: '100%', marginTop: '8px'}}
                  />
                </div>
              )}

              <div className="actions">
                {t.status !== "Done" && !t.is_blocked && (
                  <button className="btn small danger" onClick={() => setSelectedTask(t)}>Report Blocker</button>
                )}
                {t.status === "Done" && <span className="badge status-done">✓ Completed</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>

      {selectedTask && (
        <div className="modal-overlay" onClick={() => setSelectedTask(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Report Blocker</h3>
            <p><strong>{selectedTask.description}</strong></p>
            <div className="stack">
              <label>
                <div className="label-text">What's blocking this task?</div>
                <textarea 
                  value={blockerReason} 
                  onChange={(e) => setBlockerReason(e.target.value)}
                  placeholder="Describe the blocker..."
                  rows={4}
                />
              </label>
              <div className="actions">
                <button className="btn danger" onClick={() => markBlocked(selectedTask.id)} disabled={!blockerReason}>Report Blocker</button>
                <button className="btn secondary" onClick={() => setSelectedTask(null)}>Cancel</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
