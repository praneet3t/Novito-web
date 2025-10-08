import { useState, useEffect } from "react";
import { api } from "../utils/api";

export default function SprintBoard({ token }) {
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

  const columns = {
    "To Do": tasks.filter(t => t.status === "To Do"),
    "Doing": tasks.filter(t => t.status === "Doing"),
    "Submitted": tasks.filter(t => t.status === "Submitted"),
    "Done": tasks.filter(t => t.status === "Done")
  };

  if (loading) return <div className="loading-spinner"></div>;

  return (
    <div className="card">
      <h3>Sprint Board</h3>
      <div className="sprint-board">
        {Object.entries(columns).map(([status, statusTasks]) => (
          <div key={status} className="sprint-column">
            <h4>{status} ({statusTasks.length})</h4>
            {statusTasks.map(task => (
              <div key={task.id} className="task-card">
                <div className="task-card-header">
                  <div className="task-card-title">{task.description}</div>
                  {task.story_points && <span className="story-points">{task.story_points}</span>}
                </div>
                <div className="task-card-meta">
                  <span className={`badge ${task.effort_tag || 'medium'}`}>{task.effort_tag || 'N/A'}</span>
                  <span>P{task.priority}</span>
                  {task.due_date && <span>{new Date(task.due_date).toLocaleDateString()}</span>}
                </div>
                {task.is_blocked && (
                  <div className="alert danger" style={{marginTop: '8px', padding: '6px', fontSize: '11px'}}>
                    Blocked: {task.blocker_reason}
                  </div>
                )}
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
