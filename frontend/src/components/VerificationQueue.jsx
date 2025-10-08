import { useState, useEffect } from "react";
import { api } from "../utils/api";

export default function VerificationQueue({ token }) {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTask, setSelectedTask] = useState(null);
  const [verificationNotes, setVerificationNotes] = useState("");

  async function load() {
    setLoading(true);
    try {
      const data = await api.tasks.pendingVerification(token);
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

  async function handleVerify(taskId, approved) {
    try {
      await api.tasks.verify(token, taskId, { approved, verification_notes: verificationNotes });
      setSelectedTask(null);
      setVerificationNotes("");
      window.dispatchEvent(new Event("ma_refresh"));
    } catch (e) {
      alert("Failed: " + e.message);
    }
  }

  return (
    <>
      <div className="card">
        <h3>Verification Queue</h3>
        {loading ? (
          <div className="loading-spinner"></div>
        ) : (
          <div className="list">
            {tasks.length === 0 && <div className="muted">No tasks pending verification</div>}
            {tasks.map((t) => (
              <div className="item" key={t.id}>
                <div className="row">
                  <strong>{t.description}</strong>
                  <span className="badge status-submitted">Submitted</span>
                </div>
                <div className="meta">
                  Submitted: {new Date(t.submitted_at).toLocaleString()}
                </div>
                {t.submission_notes && (
                  <div className="verification-panel">
                    <strong style={{fontSize: '13px'}}>Submission Notes:</strong>
                    <p style={{marginTop: '8px', fontSize: '13px'}}>{t.submission_notes}</p>
                    {t.submission_url && (
                      <a href={t.submission_url} target="_blank" rel="noopener noreferrer" className="btn small secondary" style={{marginTop: '8px'}}>
                        View Submission
                      </a>
                    )}
                  </div>
                )}
                <div className="actions">
                  <button className="btn small success" onClick={() => setSelectedTask(t)}>Review</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {selectedTask && (
        <div className="modal-overlay" onClick={() => setSelectedTask(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Verify Task</h3>
            <p><strong>{selectedTask.description}</strong></p>
            
            <div className="verification-panel">
              <strong>Submission Details:</strong>
              <p style={{marginTop: '8px'}}>{selectedTask.submission_notes}</p>
              {selectedTask.submission_url && (
                <a href={selectedTask.submission_url} target="_blank" rel="noopener noreferrer" className="btn small secondary" style={{marginTop: '8px'}}>
                  View Submission
                </a>
              )}
            </div>

            <div className="stack" style={{marginTop: '16px'}}>
              <label>
                <div className="label-text">Verification Notes (Optional)</div>
                <textarea 
                  value={verificationNotes} 
                  onChange={(e) => setVerificationNotes(e.target.value)}
                  placeholder="Add feedback or notes..."
                  rows={3}
                />
              </label>
              <div className="actions">
                <button className="btn success" onClick={() => handleVerify(selectedTask.id, true)}>Approve</button>
                <button className="btn danger" onClick={() => handleVerify(selectedTask.id, false)}>Reject</button>
                <button className="btn secondary" onClick={() => setSelectedTask(null)}>Cancel</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
