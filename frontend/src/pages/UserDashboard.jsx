import { useState } from "react";
import MyTasks from "../components/MyTasks";
import PriorityQueue from "../components/PriorityQueue";

export default function UserDashboard({ token }) {
  const [tab, setTab] = useState("tasks");

  return (
    <>
      <div className="tabs">
        <button className={tab === "tasks" ? "active" : ""} onClick={() => setTab("tasks")}>My Tasks</button>
        <button className={tab === "queue" ? "active" : ""} onClick={() => setTab("queue")}>Priority Queue</button>
      </div>

      {tab === "tasks" && <MyTasks token={token} />}
      {tab === "queue" && <PriorityQueue token={token} />}
    </>
  );
}
