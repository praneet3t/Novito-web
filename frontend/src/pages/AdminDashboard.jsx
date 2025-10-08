import { useState } from "react";
import ProcessMeeting from "../components/ProcessMeeting";
import ManualTask from "../components/ManualTask";
import MeetingsList from "../components/MeetingsList";
import AllTasks from "../components/AllTasks";
import ReviewQueue from "../components/ReviewQueue";
import WorkCycles from "../components/WorkCycles";
import Bundles from "../components/Bundles";
import DailyBriefing from "../components/DailyBriefing";
import ProductivityAnalytics from "../components/ProductivityAnalytics";
import SprintBoard from "../components/SprintBoard";
import VerificationQueue from "../components/VerificationQueue";

export default function AdminDashboard({ token }) {
  const [tab, setTab] = useState("dashboard");

  return (
    <>
      <div className="tabs">
        <button className={tab === "dashboard" ? "active" : ""} onClick={() => setTab("dashboard")}>Dashboard</button>
        <button className={tab === "sprint" ? "active" : ""} onClick={() => setTab("sprint")}>Sprint Board</button>
        <button className={tab === "verification" ? "active" : ""} onClick={() => setTab("verification")}>Verification</button>
        <button className={tab === "overview" ? "active" : ""} onClick={() => setTab("overview")}>Overview</button>
        <button className={tab === "review" ? "active" : ""} onClick={() => setTab("review")}>Review Queue</button>
        <button className={tab === "cycles" ? "active" : ""} onClick={() => setTab("cycles")}>Work Cycles</button>
      </div>

      {tab === "dashboard" && (
        <div className="grid single">
          <DailyBriefing token={token} />
          <ProductivityAnalytics token={token} />
        </div>
      )}

      {tab === "overview" && (
        <div className="grid two-col">
          <div className="col">
            <ProcessMeeting token={token} />
            <ManualTask token={token} />
          </div>
          <div className="col">
            <MeetingsList token={token} />
            <AllTasks token={token} />
          </div>
        </div>
      )}

      {tab === "review" && <ReviewQueue token={token} />}
      {tab === "cycles" && <WorkCycles token={token} />}
      {tab === "sprint" && <SprintBoard token={token} />}
      {tab === "verification" && <VerificationQueue token={token} />}
    </>
  );
}
