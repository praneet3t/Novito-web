import { useState } from "react";
import MyTasks from "../components/MyTasks";
import PriorityQueue from "../components/PriorityQueue";
import DailyBriefing from "../components/DailyBriefing";

export default function UserDashboard({ token }) {
  const [tab, setTab] = useState("briefing");

  return (
    <>
      <div className="tabs">
        <button className={tab === "briefing" ? "active" : ""} onClick={() => setTab("briefing")}>Briefing</button>
        <button className={tab === "tasks" ? "active" : ""} onClick={() => setTab("tasks")}>My Tasks</button>
        <button className={tab === "queue" ? "active" : ""} onClick={() => setTab("queue")}>Priority Queue</button>
      </div>

      {tab === "briefing" && <DailyBriefing token={token} />}
      {tab === "tasks" && <MyTasks token={token} />}
      {tab === "queue" && <PriorityQueue token={token} />}
    </>
  );
}
