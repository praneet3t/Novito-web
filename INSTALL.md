# Installation Guide

## ✅ Completed Setup

Your Meeting Agent is now ready to use! Here's what was done:

### 1. Backend Dependencies Installed
- FastAPI 0.104.1
- Uvicorn 0.24.0
- SQLAlchemy 2.0.23
- Google Generative AI 0.3.2
- All other dependencies

### 2. Database Initialized
- SQLite database created at `meeting_agent.db`
- 7 tables created (users, tokens, meetings, tasks, work_cycles, bundle_groups, progress_snapshots)

### 3. Example Data Seeded
- 4 demo accounts created
- 2 sample meetings added
- 7 realistic tasks with priorities
- 1 active work cycle (Q1 Sprint 1)
- 1 task bundle (Authentication Feature)

## 🚀 Start the Application

### Option 1: Use Start Script (Recommended)
```bash
start.bat
```

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 🔑 Login Credentials

### Admin Account
```
Username: Admin
Password: admin123
```

### User Accounts
```
Username: Priya
Password: priya123

Username: Arjun
Password: arjun456

Username: Raghav
Password: raghav789
```

## 🎯 First Steps

1. **Open Browser**: http://localhost:5173
2. **Login as Admin**: Use Admin/admin123
3. **View Example Data**:
   - Go to "Overview" tab to see meetings and tasks
   - Go to "Review Queue" to see unapproved tasks
   - Go to "Work Cycles" to see Q1 Sprint 1
   - Go to "Bundles" to see Authentication Feature

4. **Test AI Extraction**:
   - Go to "Overview" → "Process Meeting"
   - Copy transcript from `EXAMPLE_TRANSCRIPT.md`
   - Paste and click "Process"
   - Go to "Review Queue" to see AI-extracted tasks

## 📊 What's Included

### Pre-loaded Meetings
1. **Q1 Planning Meeting** - Contains authentication tasks
2. **Sprint Retrospective** - Contains optimization tasks

### Pre-loaded Tasks (7 total)
- OAuth2 implementation (Priya, P9, Large, Doing)
- API endpoint design (Arjun, P8, Medium, To Do)
- Unit testing (Raghav, P7, Medium, To Do)
- Documentation update (Priya, P6, Small, Pending Review)
- Database optimization (Arjun, P8, Medium, Pending Review)
- CI/CD setup (Raghav, P9, Large, To Do)
- Code review (Admin, P10, Small, To Do)

### Active Work Cycle
- **Q1 Sprint 1**: 14-day sprint
- Goal: Complete authentication module and optimize API endpoints
- 5 approved tasks assigned
- View progress snapshot in "Work Cycles" tab

### Task Bundle
- **Authentication Feature**: Groups 3 auth-related tasks

## 🔧 API Documentation

Once backend is running, visit:
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## 📚 Next Steps

1. **Read Documentation**:
   - `README.md` - Full documentation
   - `QUICKSTART.md` - Quick start guide
   - `EXAMPLE_TRANSCRIPT.md` - Sample transcripts
   - `PROJECT_STRUCTURE.md` - Architecture details

2. **Test Features**:
   - Process meeting transcripts
   - Review and approve AI-extracted tasks
   - Create work cycles
   - Organize tasks into bundles
   - Track progress with snapshots

3. **Customize**:
   - Modify UI theme in `frontend/src/App.css`
   - Add new API endpoints in `backend/main.py`
   - Extend database models in `backend/database.py`

## 🐛 Troubleshooting

**Backend won't start:**
```bash
cd backend
pip install -r requirements.txt --force-reinstall
```

**Frontend won't start:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Database issues:**
```bash
cd backend
del meeting_agent.db
python -c "from database import init_db; init_db()"
python seed_data.py
```

**Port conflicts:**
- Backend uses port 8000
- Frontend uses port 5173
- Kill processes if ports are in use

## ✨ You're All Set!

Your Meeting Agent is ready to:
- ✅ Extract tasks from meeting transcripts using AI
- ✅ Manage tasks through agile workflow
- ✅ Track progress in work cycles
- ✅ Organize tasks into bundles
- ✅ Provide role-based access (admin/user)

**Start processing meetings and let AI handle the task extraction!**
