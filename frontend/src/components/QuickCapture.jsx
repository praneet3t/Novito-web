import { useState } from "react";
import { api } from "../utils/api";

export default function QuickCapture({ token }) {
  const [text, setText] = useState("");
  const [status, setStatus] = useState("");

  async function handleCapture(e) {
    e.preventDefault();
    setStatus("Processing...");
    try {
      await api.tasks.capture(token, text);
      setStatus("Task captured successfully!");
      setText("");
      setTimeout(() => setStatus(""), 3000);
      window.dispatchEvent(new Event("ma_refresh"));
    } catch (e) {
      setStatus("Failed: " + e.message);
    }
  }

  return (
    <div className="card">
      <h3>Quick Capture</h3>
      <p className="muted small">Paste a quick note or idea. AI will extract the task.</p>
      <form onSubmit={handleCapture} className="stack">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="e.g., 'Need to review the API docs by Friday' or 'Sarah should update the dashboard'"
          rows={3}
          required
        />
        <div className="actions">
          <button className="btn" type="submit" disabled={!text}>Capture Task</button>
        </div>
        {status && <div className={status.includes("success") ? "success-msg" : "muted"}>{status}</div>}
      </form>
    </div>
  );
}
