import { useState, useEffect } from "react";
import { api } from "../utils/api";

export default function DailyBriefing({ token }) {
  const [briefing, setBriefing] = useState(null);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const data = await api.analytics.briefing(token);
      setBriefing(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    const interval = setInterval(load, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, [token]);

  if (loading) return <div className="loading-spinner"></div>;
  if (!briefing) return null;

  return (
    <div className="card">
      <h3>Daily Briefing</h3>
      
      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-value">{briefing.completed_today}</div>
          <div className="stat-label">Completed Today</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{color: briefing.blocked_count > 0 ? 'var(--danger)' : 'var(--success)'}}>
            {briefing.blocked_count}
          </div>
          <div className="stat-label">Blocked Tasks</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{color: briefing.overdue_count > 0 ? 'var(--warning)' : 'var(--success)'}}>
            {briefing.overdue_count}
          </div>
          <div className="stat-label">Overdue</div>
        </div>
      </div>

      {briefing.blocked_count > 0 && (
        <div className="alert danger">
          <span>ALERT</span>
          <div>
            <strong>{briefing.blocked_count} tasks are blocked</strong>
            {briefing.blocked_tasks.map(t => (
              <div key={t.id} className="small">{t.description} - {t.reason}</div>
            ))}
          </div>
        </div>
      )}

      {briefing.overdue_count > 0 && (
        <div className="alert warning">
          <span>WARNING</span>
          <div>
            <strong>{briefing.overdue_count} tasks are overdue</strong>
            {briefing.overdue_tasks.map(t => (
              <div key={t.id} className="small">{t.description} (Due: {t.due_date})</div>
            ))}
          </div>
        </div>
      )}

      {briefing.risk_count > 0 && (
        <div className="alert warning">
          <span>RISK</span>
          <div>
            <strong>{briefing.risk_count} tasks have potential risks</strong>
            {briefing.risk_tasks.map(t => (
              <div key={t.id} className="small">{t.description} - {t.reason}</div>
            ))}
          </div>
        </div>
      )}

      {briefing.pending_approval > 0 && (
        <div className="alert info">
          <span>INFO</span>
          <div>
            <strong>{briefing.pending_approval} tasks need manager approval</strong>
          </div>
        </div>
      )}

      {briefing.sla_breached > 0 && (
        <div className="alert danger">
          <span>SLA BREACH</span>
          <div>
            <strong>{briefing.sla_breached} tasks exceeded verification deadline</strong>
          </div>
        </div>
      )}

      {briefing.high_priority.length > 0 && (
        <div style={{marginTop: '16px'}}>
          <strong>Top Priorities:</strong>
          {briefing.high_priority.map(t => (
            <div key={t.id} className="chip" style={{margin: '4px'}}>
              P{t.priority}: {t.description}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
