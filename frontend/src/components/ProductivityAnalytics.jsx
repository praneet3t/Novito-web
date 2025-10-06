import { useState, useEffect } from "react";
import { api } from "../utils/api";

export default function ProductivityAnalytics({ token }) {
  const [analytics, setAnalytics] = useState(null);
  const [days, setDays] = useState(7);

  async function load() {
    try {
      const data = await api.analytics.productivity(token, days);
      setAnalytics(data);
    } catch (e) {
      console.error(e);
    }
  }

  useEffect(() => { load(); }, [token, days]);

  if (!analytics) return <div className="loading-spinner"></div>;

  return (
    <div className="card">
      <h3>📈 Productivity Analytics</h3>
      
      <div style={{marginBottom: '16px'}}>
        <label className="inline">
          Period:
          <select value={days} onChange={(e) => setDays(Number(e.target.value))} style={{marginLeft: '8px', width: 'auto'}}>
            <option value={7}>Last 7 days</option>
            <option value={14}>Last 14 days</option>
            <option value={30}>Last 30 days</option>
          </select>
        </label>
      </div>

      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-value">{analytics.meetings_held}</div>
          <div className="stat-label">Meetings Held</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{analytics.completion_rate}%</div>
          <div className="stat-label">Completion Rate</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{analytics.avg_completion_hours}h</div>
          <div className="stat-label">Avg Completion Time</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{color: analytics.blocker_rate > 20 ? 'var(--danger)' : 'var(--success)'}}>
            {analytics.blocker_rate}%
          </div>
          <div className="stat-label">Blocker Rate</div>
        </div>
      </div>

      <div style={{marginTop: '16px'}}>
        <div className="muted small">Task Completion</div>
        <div className="progress-bar">
          <div className="progress-fill" style={{width: `${analytics.completion_rate}%`}}></div>
        </div>
        <div className="muted small">{analytics.completed_tasks} of {analytics.total_tasks} tasks completed</div>
      </div>

      {analytics.blocker_rate > 20 && (
        <div className="alert warning" style={{marginTop: '16px'}}>
          <span>⚠️</span>
          <span>High blocker rate detected. Consider reviewing team dependencies and resources.</span>
        </div>
      )}
    </div>
  );
}
