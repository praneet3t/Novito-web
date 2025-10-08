import { useState, useEffect } from "react";
import { api } from "../utils/api";

export default function DailyShutdownModal({ token }) {
  const [show, setShow] = useState(false);
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    const checkTime = () => {
      const now = new Date();
      const hour = now.getHours();
      const minute = now.getMinutes();
      
      if (hour === 17 && minute === 0) {
        loadIncompleteTasks();
        setShow(true);
      }
    };

    const interval = setInterval(checkTime, 60000);
    return () => clearInterval(interval);
  }, []);

  async function loadIncompleteTasks() {
    try {
      const data = await api.tasks.my(token);
      const incomplete = data.filter(t => t.status !== "Done" && t.progress < 100);
      setTasks(incomplete);
    } catch (e) {
      console.error(e);
    }
  }

  async function planForTomorrow() {
    try {
      await api.tasks.planTomorrow(token);
      setShow(false);
      window.dispatchEvent(new Event("ma_refresh"));
    } catch (e) {
      alert("Failed: " + e.message);
    }
  }

  if (!show) return null;

  return (
    <div className="modal-overlay">
      <div className="modal">
        <h3>Daily Shutdown Ritual</h3>
        <p>You have {tasks.length} incomplete tasks. Plan them for tomorrow?</p>
        
        <div className="list" style={{maxHeight: '300px', overflow: 'auto', marginTop: '16px'}}>
          {tasks.map(t => (
            <div key={t.id} className="chip" style={{display: 'block', marginBottom: '8px'}}>
              {t.description} ({t.progress}%)
            </div>
          ))}
        </div>

        <div className="actions" style={{marginTop: '16px'}}>
          <button className="btn success" onClick={planForTomorrow}>Plan for Tomorrow</button>
          <button className="btn secondary" onClick={() => setShow(false)}>Dismiss</button>
        </div>
      </div>
    </div>
  );
}
