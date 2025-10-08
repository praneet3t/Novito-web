import { useState } from "react";
import MyTasks from "../components/MyTasks";
import PriorityQueue from "../components/PriorityQueue";
import DailyBriefing from "../components/DailyBriefing";
import QuickCapture from "../components/QuickCapture";
import NotificationPanel from "../components/NotificationPanel";
import DailyShutdownModal from "../components/DailyShutdownModal";

export default function UserDashboard({ token }) {
  const [tab, setTab] = useState("briefing");

  return (
    <>
      <div className="tabs">
        <button className={tab === "briefing" ? "active" : ""} onClick={() => setTab("briefing")}>Briefing</button>
        <button className={tab === "tasks" ? "active" : ""} onClick={() => setTab("tasks")}>My Tasks</button>
        <button className={tab === "queue" ? "active" : ""} onClick={() => setTab("queue")}>Priority Queue</button>
        <button className={tab === "notifications" ? "active" : ""} onClick={() => setTab("notifications")}>Notifications</button>
      </div>

      {tab === "briefing" && (
        <div className="grid two-col">
          <DailyBriefing token={token} />
          <QuickCapture token={token} />
        </div>
      )}
      {tab === "tasks" && <MyTasks token={token} />}
      {tab === "queue" && <PriorityQueue token={token} />}
      {tab === "notifications" && <NotificationPanel token={token} />}
      
      <DailyShutdownModal token={token} />
    </>
  );
}
