import { useState, useEffect } from "react";
import { api } from "../utils/api";

export default function WorkCycles({ token }) {
  const [cycles, setCycles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState("");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [goal, setGoal] = useState("");
  const [selected, setSelected] = useState(null);
  const [snapshot, setSnapshot] = useState(null);

  async function load() {
    setLoading(true);
    try {
      const data = await api.workcycles.list(token);
      setCycles(data);
    } catch (e) {
      setCycles([]);
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

  async function create(e) {
    e.preventDefault();
    try {
      await api.workcycles.create(token, { name, start_date: start, end_date: end, goal });
      setName("");
      setStart("");
      setEnd("");
      setGoal("");
      window.dispatchEvent(new Event("ma_refresh"));
    } catch (e) {
      alert("Failed: " + e.message);
    }
  }

  async function viewSnapshot(id) {
    try {
      const data = await api.workcycles.snapshot(token, id);
      setSnapshot(data);
      setSelected(id);
    } catch (e) {
      alert("Failed: " + e.message);
    }
  }

  return (
    <div className="grid two-col">
      <div className="card">
        <h3>Create Work Cycle</h3>
        <form onSubmit={create} className="stack">
          <label>
            <div className="label-text">Name</div>
            <input value={name} onChange={(e) => setName(e.target.value)} required />
          </label>
          <label>
            <div className="label-text">Start Date</div>
            <input value={start} onChange={(e) => setStart(e.target.value)} required />
          </label>
          <label>
            <div className="label-text">End Date</div>
            <input value={end} onChange={(e) => setEnd(e.target.value)} required />
          </label>
          <label>
            <div className="label-text">Goal</div>
            <textarea value={goal} onChange={(e) => setGoal(e.target.value)} rows={3}></textarea>
          </label>
          <div className="actions">
            <button className="btn" type="submit">Create</button>
          </div>
        </form>
      </div>

      <div className="card">
        <h3>Work Cycles</h3>
        {loading ? (
          <div className="muted">Loading...</div>
        ) : (
          <div className="list">
            {cycles.length === 0 && <div className="muted">No cycles</div>}
            {cycles.map((c) => (
              <div className="item" key={c.id}>
                <strong>{c.name}</strong>
                <div className="muted small">
                  {c.start_date} → {c.end_date}
                </div>
                {c.goal && <p className="muted">{c.goal}</p>}
                <div className="actions">
                  <button className="btn small" onClick={() => viewSnapshot(c.id)}>View Snapshot</button>
                </div>
              </div>
            ))}
          </div>
        )}

        {snapshot && selected && (
          <div className="snapshot">
            <h4>{snapshot.cycle_name}</h4>
            <div className="stat-grid">
              <div className="stat-card">
                <div className="stat-value">{snapshot.completed_items}/{snapshot.total_items}</div>
                <div className="stat-label">Tasks Completed</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{snapshot.remaining_effort}/{snapshot.total_effort}</div>
                <div className="stat-label">Effort Points</div>
              </div>
            </div>
            {snapshot.blockers.length > 0 && (
              <div style={{marginTop: '16px'}}>
                <strong style={{color: 'var(--danger)'}}>Blockers:</strong>
                {snapshot.blockers.map((b) => (
                  <div key={b.id} className="muted small" style={{marginTop: '8px'}}>• {b.description}</div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
