# Where to Find Each Enterprise Feature

## Login First
```
Admin: Admin / admin123
User:  Priya / priya123
```

## Feature 1: AI Proactive Scheduling
**Location:** Any task detail view
**What to see:** Each task has a `suggested_focus_time` calculated based on effort
- Small tasks: 1 hour before due date
- Medium tasks: 3 hours before due date  
- Large tasks: 6 hours before due date

**Example Task:** "Implement OAuth2 login flow" (Large, due in 3 days)
- Suggested focus time: 3 days from now - 6 hours

## Feature 2: Contextual Risk Detection
**Location:** Admin Dashboard → Dashboard Tab
**What to see:** Daily Briefing shows "RISK" alert

**Example Task:** "Integrate payment gateway API"
- Status: Flagged as potential risk
- Reason: "Waiting for payment provider API credentials"
- Shows in Daily Briefing with warning

## Feature 3: Manual Natural Language Capture
**Location:** 
- **Admin:** Capture Inbox tab
- **User:** Briefing tab (right side)

**How to test:**
1. Type: "Need to review API docs by Friday"
2. Click "Capture Task"
3. AI extracts task and puts in "Capture Inbox" status

**Example Task:** "Research new UI framework options"
- Status: Capture Inbox
- Awaiting planning/review

## Feature 4: Confidence-Based Priority
**Location:** Admin Dashboard → Review Queue tab
**What to see:** Tasks with low confidence (<0.7) automatically set to P4

**Example Task:** "Update API documentation"
- Confidence: 0.6 (60%)
- Priority: Automatically set to 4 (Low)
- Flag: needs_priority_review = True

## Feature 5: No-Code Approval Workflows
**Location:** Admin Dashboard → Dashboard Tab (bottom right)
**What to see:** "Manager Approval Queue" component

**Example Task:** "Refactor entire authentication system"
- Story Points: 21 (>8 threshold)
- Status: "Manager Approval Pending"
- Admin must approve before it moves to "To Do"

**How to test:**
1. Click "Approve" button
2. Task moves to "To Do" status
3. Notification sent to assignee

## Feature 6: Custom SLA Tracking
**Location:** Admin Dashboard → Dashboard Tab
**What to see:** Daily Briefing shows "SLA BREACH" alert

**Example Task:** "Setup database migrations"
- Status: Submitted 12 hours ago
- Verification deadline: 12 hours from now
- If not verified in time: SLA breach flag

**How to test:**
1. Go to Verification tab
2. See task with deadline
3. If deadline passes: Shows in SLA breach alert

## Feature 7: User Group Management
**Location:** Database (Teams created)
**What to see:** Tasks associated with teams

**Example Teams:**
- Frontend Team: Priya
- Backend Team: Arjun (lead), Raghav

**Example Tasks:**
- "Implement OAuth2" → Frontend Team
- "Design API endpoints" → Backend Team

## Feature 8: Real-Time Status Notifications
**Location:** User Dashboard → Notifications Tab
**What to see:** List of system notifications

**Example Notifications:**
- "Task submitted for review: Setup database migrations"
- "Risk detected: Integrate payment gateway - Waiting for credentials"
- "Manager approval required: Refactor authentication (21 story points)"
- "Welcome to Meeting Agent! Check out Quick Capture feature"

**How to test:**
1. Submit a task (as user)
2. Check notifications tab
3. See "Task submitted" notification
4. Click "Mark Read"

## Feature 9: Daily Shutdown Ritual
**Location:** User Dashboard (Auto-appears at 5:00 PM)
**What to see:** Modal with incomplete tasks

**Example Task:** "Fix responsive layout issues"
- Status: "Planned for Tomorrow"
- Progress: 30%

**How to test:**
1. Wait until 5:00 PM (or modify time in code for testing)
2. Modal appears automatically
3. Shows all incomplete tasks
4. Click "Plan for Tomorrow"
5. All tasks moved to "Planned for Tomorrow" status

## Feature 10: Time Blocking on Calendar
**Location:** User Dashboard → My Tasks Tab (right side)
**What to see:** Monthly calendar with tasks on due dates

**Features:**
- Click on any date to see tasks due that day
- Tasks with due dates show on calendar
- Visual task count badges
- Today highlighted
- Weekend differentiation

**Example:**
- Tasks distributed across month
- Click date to see: "Implement OAuth2 (due in 3 days)"

---

## Quick Test Checklist

### As Admin (Admin/admin123):
1. ✅ Dashboard Tab → See Daily Briefing with risks, SLA breaches
2. ✅ Dashboard Tab → See Manager Approval Queue (1 task)
3. ✅ Verification Tab → See submitted task with deadline
4. ✅ Capture Inbox Tab → See captured task + Quick Capture form
5. ✅ Review Queue Tab → See low-confidence task (P4)

### As User (Priya/priya123):
1. ✅ Briefing Tab → See Quick Capture form (right side)
2. ✅ My Tasks Tab → See calendar with tasks (right side)
3. ✅ My Tasks Tab → See task at 100% with "Submit for Review" button
4. ✅ Notifications Tab → See 2-3 notifications
5. ✅ Wait for 5 PM → Daily Shutdown Modal appears

---

## Visual Guide

### Admin Dashboard Layout:
```
Dashboard Tab:
┌─────────────────────────────────────────┐
│ Daily Briefing                          │
│ - Completed Today: X                    │
│ - Blocked: X                            │
│ - RISK ALERT: Payment gateway task      │
│ - SLA BREACH: Database migrations       │
│ - Manager Approval Needed: 1            │
├─────────────────┬───────────────────────┤
│ Productivity    │ Manager Approval      │
│ Analytics       │ Queue                 │
│                 │ - Refactor auth (21SP)│
└─────────────────┴───────────────────────┘
```

### User Dashboard Layout:
```
My Tasks Tab:
┌─────────────────────────┬───────────────┐
│ Task List               │ Calendar      │
│ - OAuth2 (60% done)     │  Jan 2024     │
│ - Login UI (100%)       │ ┌───┬───┬───┐ │
│   [Submit for Review]   │ │ 1 │ 2 │ 3 │ │
│                         │ ├───┼───┼───┤ │
│                         │ │ 4 │ 5 │ 6 │ │
│                         │ └───┴───┴───┘ │
└─────────────────────────┴───────────────┘

Notifications Tab:
┌─────────────────────────────────────────┐
│ Notifications (2 unread)                │
│ ● Task submitted for review             │
│ ● Welcome to Meeting Agent              │
└─────────────────────────────────────────┘
```

---

## All Features Are Now Visible!

Start the application and login to see all 10 enterprise features in action with real example data.
