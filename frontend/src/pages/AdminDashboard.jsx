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
import QuickCapture from "../components/QuickCapture";
import CaptureInbox from "../components/CaptureInbox";
import NotificationPanel from "../components/NotificationPanel";
import ManagerApproval from "../components/ManagerApproval";

export default function AdminDashboard({ token }) {
  const [tab, setTab] = useState("dashboard");

  return (
    <>
      <div className="tabs">
        <button className={tab === "dashboard" ? "active" : ""} onClick={() => setTab("dashboard")}>Dashboard</button>
        <button className={tab === "sprint" ? "active" : ""} onClick={() => setTab("sprint")}>Sprint Board</button>
        <button className={tab === "verification" ? "active" : ""} onClick={() => setTab("verification")}>Verification</button>
        <button className={tab === "capture" ? "active" : ""} onClick={() => setTab("capture")}>Capture Inbox</button>
        <button className={tab === "overview" ? "active" : ""} onClick={() => setTab("overview")}>Overview</button>
        <button className={tab === "review" ? "active" : ""} onClick={() => setTab("review")}>Review Queue</button>
        <button className={tab === "cycles" ? "active" : ""} onClick={() => setTab("cycles")}>Work Cycles</button>
      </div>



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
      {tab === "capture" && (
        <div className="grid two-col">
          <CaptureInbox token={token} />
          <QuickCapture token={token} />
        </div>
      )}

      {tab === "dashboard" && (
        <div className="grid single">
          <DailyBriefing token={token} />
          <div className="grid two-col">
            <ProductivityAnalytics token={token} />
            <ManagerApproval token={token} />
          </div>
        </div>
      )}
    </>
  );
}
