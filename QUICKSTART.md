# 🚀 Quick Start Guide

Get Meeting Agent running in 3 minutes!

## Step 1: Setup (One-time)

Double-click `setup.bat` or run:
```bash
setup.bat
```

This will:
- ✓ Install Python dependencies
- ✓ Install Node.js dependencies  
- ✓ Create database
- ✓ Seed example data

## Step 2: Start Servers

Double-click `start.bat` or run:
```bash
start.bat
```

This will:
- ✓ Start backend server (port 8000)
- ✓ Start frontend server (port 5173)
- ✓ Open browser automatically

## Step 3: Login & Test

### Login as Admin
```
Username: Admin
Password: admin123
```

### Test AI Task Extraction

1. Click **"Overview"** tab
2. In **"Process Meeting"** section:
   - Title: `Sprint Planning`
   - Transcript: Copy from `EXAMPLE_TRANSCRIPT.md`
3. Click **"Process"**
4. Go to **"Review Queue"** tab
5. See AI-extracted tasks with priorities and effort estimates
6. Adjust values and click **"Approve"**

### View Example Data

The system comes with pre-loaded examples:

**Meetings Tab:**
- Q1 Planning Meeting
- Sprint Retrospective

**Review Queue Tab:**
- 2 unapproved tasks waiting for review

**Work Cycles Tab:**
- Q1 Sprint 1 (active)
- Click "View Snapshot" to see progress

**Bundles Tab:**
- Authentication Feature bundle

### Test User View

1. Logout (top-right)
2. Login as user:
   ```
   Username: Priya
   Password: priya123
   ```
3. View **"My Tasks"** - See assigned tasks
4. View **"Priority Queue"** - See approved tasks by priority
5. Click **"Mark Done"** to complete tasks

## 🎯 Key Features to Try

### 1. AI Task Extraction
Paste this in transcript field:
```
Priya: I'll implement the login page by Friday.
Arjun: I can handle the API integration, needs 3 days.
Raghav: I'll write tests after Arjun is done.
```

AI will extract:
- 3 tasks with assignees
- Estimated deadlines
- Priority levels
- Effort estimates

### 2. Review & Approve Workflow
1. Admin reviews AI-extracted tasks
2. Adjusts priority (1-10)
3. Sets effort (small/medium/large)
4. Approves → Moves to priority queue

### 3. Work Cycles (Sprints)
1. Create cycle with dates and goal
2. Assign approved tasks to cycle
3. View snapshot for progress metrics
4. Track completed vs remaining effort

### 4. Task Bundles
1. Create bundle (e.g., "Login Feature")
2. Group related tasks
3. View all tasks in bundle

## 📊 Understanding the UI

### Admin Dashboard Tabs
- **Overview**: Process meetings, create tasks, view all data
- **Review Queue**: Approve AI-extracted tasks
- **Work Cycles**: Manage sprints and track progress
- **Bundles**: Organize tasks into groups

### User Dashboard Tabs
- **My Tasks**: Personal task list
- **Priority Queue**: Approved tasks sorted by priority

### Task Badges
- 🔵 **Small**: Quick tasks (< 1 day)
- 🟡 **Medium**: Standard tasks (1-3 days)
- 🔴 **Large**: Complex tasks (> 3 days)

### Priority Levels
- **P10**: Critical/Blocking
- **P8-9**: High priority
- **P5-7**: Medium priority
- **P1-4**: Low priority

## 🔧 Troubleshooting

**Port already in use:**
```bash
# Kill processes on ports 8000 and 5173
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Database locked:**
```bash
# Delete and recreate
del meeting_agent.db
python -c "from database import init_db; init_db()"
python -c "from seed_data import seed_example_data; seed_example_data()"
```

**AI not working:**
- Check `.env` file has `GEMINI_API_KEY`
- Verify API key at https://makersuite.google.com/

## 📚 Next Steps

- Read full `README.md` for detailed documentation
- Check `EXAMPLE_TRANSCRIPT.md` for more test transcripts
- Explore API docs at http://127.0.0.1:8000/docs
- Customize UI in `frontend/src/App.css`

## 🎉 You're Ready!

Start processing meetings and let AI handle the task extraction!
