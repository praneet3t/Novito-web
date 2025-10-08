import { useState, useEffect } from "react";
import { api } from "../utils/api";

export default function NotificationPanel({ token }) {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const data = await api.notifications.list(token);
      setNotifications(data);
    } catch (e) {
      setNotifications([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    const interval = setInterval(load, 30000);
    return () => clearInterval(interval);
  }, [token]);

  async function markRead(id) {
    try {
      await api.notifications.markRead(token, id);
      load();
    } catch (e) {
      console.error(e);
    }
  }

  const unread = notifications.filter(n => !n.is_read);

  return (
    <div className="card">
      <h3>Notifications {unread.length > 0 && <span className="badge danger">{unread.length}</span>}</h3>
      {loading ? (
        <div className="loading-spinner"></div>
      ) : (
        <div className="list">
          {notifications.length === 0 && <div className="muted">No notifications</div>}
          {notifications.slice(0, 10).map(n => (
            <div key={n.id} className="item" style={{opacity: n.is_read ? 0.6 : 1}}>
              <div className="row">
                <div style={{fontSize: '13px'}}>{n.message}</div>
                {!n.is_read && (
                  <button className="btn small secondary" onClick={() => markRead(n.id)}>Mark Read</button>
                )}
              </div>
              <div className="muted small">{new Date(n.created_at).toLocaleString()}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
