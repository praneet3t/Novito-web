import { useState } from "react";
import { api } from "../utils/api";

export default function ManualTask({ token }) {
  const [desc, setDesc] = useState("");
  const [meetingId, setMeetingId] = useState("");
  const [assignee, setAssignee] = useState("");
  const [due, setDue] = useState("");
  const [effort, setEffort] = useState("");
  const [priority, setPriority] = useState(0);
  const [status, setStatus] = useState("");

  async function handleCreate(e) {
    e.preventDefault();
    setStatus("Creating...");
    try {
      const t = await api.tasks.create(token, {
        description: desc,
        meeting_id: Number(meetingId),
        assignee_username: assignee,
        due_date: due || null,
        effort_tag: effort || null,
        priority: Number(priority),
      });
      setStatus("Task created: " + t.id);
      setDesc("");
      setMeetingId("");
      setAssignee("");
      setDue("");
      setEffort("");
      setPriority(0);
      window.dispatchEvent(new Event("ma_refresh"));
    } catch (e) {
      setStatus(e.message);
    }
  }

  return (
    <div className="card">
      <h3>Create Task</h3>
      <form onSubmit={handleCreate} className="stack">
        <label>
          <div className="label-text">Description</div>
          <input value={desc} onChange={(e) => setDesc(e.target.value)} required />
        </label>
        <label>
          <div className="label-text">Meeting ID</div>
          <input value={meetingId} onChange={(e) => setMeetingId(e.target.value)} required />
        </label>
        <label>
          <div className="label-text">Assignee</div>
          <input value={assignee} onChange={(e) => setAssignee(e.target.value)} required />
        </label>
        <label>
          <div className="label-text">Due (optional)</div>
          <input value={due} onChange={(e) => setDue(e.target.value)} />
        </label>
        <label>
          <div className="label-text">Effort</div>
          <select value={effort} onChange={(e) => setEffort(e.target.value)}>
            <option value="">None</option>
            <option value="small">Small</option>
            <option value="medium">Medium</option>
            <option value="large">Large</option>
          </select>
        </label>
        <label>
          <div className="label-text">Priority</div>
          <input type="number" value={priority} onChange={(e) => setPriority(e.target.value)} />
        </label>
        <div className="actions">
          <button className="btn" type="submit">Create</button>
        </div>
        {status && <div className="muted">{status}</div>}
      </form>
    </div>
  );
}
