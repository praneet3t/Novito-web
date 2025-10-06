import { useState, useEffect } from "react";
import { api } from "../utils/api";

export default function MeetingsList({ token }) {
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const data = await api.meetings.list(token);
      setMeetings(data);
    } catch (e) {
      setMeetings([]);
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
      <h3>Meetings</h3>
      {loading ? (
        <div className="muted">Loading...</div>
      ) : (
        <div className="list">
          {meetings.length === 0 && <div className="muted">No meetings</div>}
          {meetings.map((m) => (
            <div className="item" key={m.id}>
              <div className="item-head">
                <strong>{m.title}</strong>
                <div className="muted small">{m.date}</div>
              </div>
              {m.summary_minutes && <p className="summary">{m.summary_minutes}</p>}
              <div className="meta">ID: {m.id}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
