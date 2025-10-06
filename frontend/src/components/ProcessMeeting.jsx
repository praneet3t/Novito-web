import { useState } from "react";
import { api } from "../utils/api";

export default function ProcessMeeting({ token }) {
  const [title, setTitle] = useState("");
  const [date, setDate] = useState("");
  const [transcript, setTranscript] = useState("");
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setStatus("Processing...");
    try {
      const fd = new FormData();
      fd.append("title", title);
      if (date) fd.append("date", date);
      if (transcript) fd.append("transcript", transcript);
      if (file) fd.append("file", file);

      const mt = await api.meetings.process(token, fd);
      setStatus("Processed: " + mt.title);
      setTitle("");
      setTranscript("");
      setFile(null);
      setDate("");
      window.dispatchEvent(new Event("ma_refresh"));
    } catch (e) {
      setStatus(e.message);
    }
  }

  return (
    <div className="card">
      <h3>Process Meeting</h3>
      <form onSubmit={handleSubmit} className="stack">
        <label>
          <div className="label-text">Title</div>
          <input value={title} onChange={(e) => setTitle(e.target.value)} required />
        </label>
        <label>
          <div className="label-text">Date (ISO)</div>
          <input value={date} onChange={(e) => setDate(e.target.value)} />
        </label>
        <label>
          <div className="label-text">Transcript</div>
          <textarea value={transcript} onChange={(e) => setTranscript(e.target.value)} rows={6}></textarea>
        </label>
        <label>
          <div className="label-text">Upload audio (optional)</div>
          <input type="file" accept="audio/*" onChange={(e) => setFile(e.target.files[0])} />
        </label>
        <div className="actions">
          <button className="btn" type="submit">Process</button>
        </div>
        {status && <div className="muted">{status}</div>}
      </form>
    </div>
  );
}
