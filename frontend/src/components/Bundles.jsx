import { useState, useEffect } from "react";
import { api } from "../utils/api";

export default function Bundles({ token }) {
  const [bundles, setBundles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [title, setTitle] = useState("");
  const [desc, setDesc] = useState("");
  const [selected, setSelected] = useState(null);
  const [tasks, setTasks] = useState([]);

  async function load() {
    setLoading(true);
    try {
      const data = await api.bundles.list(token);
      setBundles(data);
    } catch (e) {
      setBundles([]);
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
      await api.bundles.create(token, { title, description: desc });
      setTitle("");
      setDesc("");
      window.dispatchEvent(new Event("ma_refresh"));
    } catch (e) {
      alert("Failed: " + e.message);
    }
  }

  async function viewTasks(id) {
    try {
      const data = await api.bundles.tasks(token, id);
      setTasks(data);
      setSelected(id);
    } catch (e) {
      alert("Failed: " + e.message);
    }
  }

  return (
    <div className="grid two-col">
      <div className="card">
        <h3>Create Bundle</h3>
        <form onSubmit={create} className="stack">
          <label>
            <div className="label-text">Title</div>
            <input value={title} onChange={(e) => setTitle(e.target.value)} required />
          </label>
          <label>
            <div className="label-text">Description</div>
            <textarea value={desc} onChange={(e) => setDesc(e.target.value)} rows={3}></textarea>
          </label>
          <div className="actions">
            <button className="btn" type="submit">Create</button>
          </div>
        </form>
      </div>

      <div className="card">
        <h3>Bundles</h3>
        {loading ? (
          <div className="muted">Loading...</div>
        ) : (
          <div className="list">
            {bundles.length === 0 && <div className="muted">No bundles</div>}
            {bundles.map((b) => (
              <div className="item" key={b.id}>
                <strong>{b.title}</strong>
                {b.description && <p className="muted">{b.description}</p>}
                <div className="actions">
                  <button className="btn small" onClick={() => viewTasks(b.id)}>View Tasks</button>
                </div>
              </div>
            ))}
          </div>
        )}

        {selected && tasks.length > 0 && (
          <div className="tasks-list">
            <h4>Bundle Tasks</h4>
            {tasks.map((t) => (
              <div key={t.id} className="muted small">- {t.description}</div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
