# 📁 Project Structure

```
Novito-web/
│
├── 📄 README.md                    # Full documentation
├── 📄 QUICKSTART.md                # Quick start guide
├── 📄 EXAMPLE_TRANSCRIPT.md        # Sample meeting transcripts
├── 📄 PROJECT_STRUCTURE.md         # This file
├── 📄 .env                         # Environment variables (GEMINI_API_KEY)
├── 📄 .gitignore                   # Git ignore rules
├── 📄 setup.bat                    # One-time setup script
├── 📄 start.bat                    # Start servers script
├── 📄 meeting_agent.db             # SQLite database (auto-generated)
│
├── 📂 backend/                     # Python FastAPI Backend
│   ├── 📄 main.py                  # FastAPI app & API endpoints
│   ├── 📄 database.py              # SQLAlchemy models & DB config
│   ├── 📄 gemini_service.py        # AI task extraction service
│   ├── 📄 seed_data.py             # Example data generator
│   ├── 📄 requirements.txt         # Python dependencies
│   └── 📄 __init__.py              # Package marker
│
└── 📂 frontend/                    # React + Vite Frontend
    ├── 📂 src/
    │   ├── 📂 components/          # Reusable React components
    │   │   ├── 📄 AllTasks.jsx         # Admin: View all tasks
    │   │   ├── 📄 Bundles.jsx          # Admin: Manage task bundles
    │   │   ├── 📄 ManualTask.jsx       # Admin: Create tasks manually
    │   │   ├── 📄 MeetingsList.jsx     # Admin: View all meetings
    │   │   ├── 📄 MyTasks.jsx          # User: Personal task list
    │   │   ├── 📄 PriorityQueue.jsx    # User: Approved tasks by priority
    │   │   ├── 📄 ProcessMeeting.jsx   # Admin: Process transcripts
    │   │   ├── 📄 ReviewQueue.jsx      # Admin: Approve AI tasks
    │   │   └── 📄 WorkCycles.jsx       # Admin: Manage sprints
    │   │
    │   ├── 📂 pages/               # Page-level components
    │   │   ├── 📄 AdminDashboard.jsx   # Admin main view
    │   │   ├── 📄 LoginPage.jsx        # Authentication page
    │   │   └── 📄 UserDashboard.jsx    # User main view
    │   │
    │   ├── 📂 hooks/               # Custom React hooks
    │   │   └── 📄 useAuth.js           # Authentication state management
    │   │
    │   ├── 📂 utils/               # Utility functions
    │   │   └── 📄 api.js               # Centralized API client
    │   │
    │   ├── 📄 App.jsx              # Main app component
    │   ├── 📄 App.css              # Professional dark theme styles
    │   └── 📄 main.jsx             # React entry point
    │
    ├── 📄 index.html               # HTML template
    ├── 📄 package.json             # Node dependencies
    ├── 📄 package-lock.json        # Locked dependencies
    └── 📄 vite.config.js           # Vite configuration
```

## 🔑 Key Files Explained

### Backend Core

**`main.py`** (500+ lines)
- FastAPI application setup
- 20+ API endpoints
- Authentication middleware
- CORS configuration
- Request/response models

**`database.py`** (200+ lines)
- SQLAlchemy ORM models:
  - User, Token, Meeting, Task
  - WorkCycle, BundleGroup, ProgressSnapshot
- Database initialization
- Session management
- Seed user creation

**`gemini_service.py`** (50 lines)
- Google Gemini AI integration
- Task extraction from transcripts
- Meeting summarization
- Structured JSON output

**`seed_data.py`** (100 lines)
- Creates example users
- Generates sample meetings
- Creates work cycles and bundles
- Populates realistic tasks

### Frontend Core

**`App.jsx`** (30 lines)
- Main application component
- Route logic (login vs dashboard)
- Header with user info
- Footer

**`api.js`** (100 lines)
- Centralized API calls
- Error handling
- Token management
- Endpoints for:
  - Auth, Meetings, Tasks
  - WorkCycles, Bundles

**`useAuth.js`** (30 lines)
- Custom React hook
- LocalStorage persistence
- Login/logout logic
- User state management

**`App.css`** (200 lines)
- Professional dark theme
- CSS variables for theming
- Responsive grid layouts
- Component styles
- Animations & transitions

### Component Breakdown

**Admin Components:**
- `ProcessMeeting.jsx` - Upload transcripts, trigger AI
- `ReviewQueue.jsx` - Approve/edit AI-extracted tasks
- `WorkCycles.jsx` - Create sprints, view progress
- `Bundles.jsx` - Group related tasks
- `AllTasks.jsx` - View all system tasks
- `MeetingsList.jsx` - View all meetings
- `ManualTask.jsx` - Create tasks without AI

**User Components:**
- `MyTasks.jsx` - Personal assigned tasks
- `PriorityQueue.jsx` - Approved tasks by priority

**Shared:**
- `LoginPage.jsx` - Authentication form

## 🗄️ Database Schema

### Tables

**users**
- id, username, password, is_admin, created_at

**tokens**
- id, token, user_id, expires_at

**meetings**
- id, title, date, summary_minutes, processed_by_id, created_at

**tasks**
- id, description, due_date, status, priority
- effort_tag, confidence, timestamp_seconds, is_approved
- assignee_id, meeting_id, bundle_id, workcycle_id, created_at

**work_cycles**
- id, name, start_date, end_date, goal, owner_id, created_at

**bundle_groups**
- id, title, description, owner_id, created_at

**progress_snapshots**
- id, workcycle_id, snapshot_date, remaining_effort, created_at

## 🔄 Data Flow

### Meeting Processing Flow
```
1. Admin uploads transcript
   ↓
2. Backend receives via POST /meetings/process
   ↓
3. Gemini AI extracts tasks
   ↓
4. Tasks saved with is_approved=False
   ↓
5. Admin reviews in Review Queue
   ↓
6. Admin approves → is_approved=True
   ↓
7. Tasks appear in Priority Queue
   ↓
8. Users pick tasks and complete them
```

### Authentication Flow
```
1. User enters credentials
   ↓
2. POST /auth/login
   ↓
3. Backend validates & creates token
   ↓
4. Token stored in localStorage
   ↓
5. Token sent in Authorization header
   ↓
6. Backend validates token on each request
```

## 🎨 UI Component Hierarchy

```
App
├── Header (topbar)
│   ├── Brand
│   └── User Info + Logout
│
├── Main Container
│   ├── LoginPage (if not authenticated)
│   │   └── Login Form
│   │
│   ├── AdminDashboard (if admin)
│   │   ├── Tabs Navigation
│   │   ├── Overview Tab
│   │   │   ├── ProcessMeeting
│   │   │   ├── ManualTask
│   │   │   ├── MeetingsList
│   │   │   └── AllTasks
│   │   ├── Review Queue Tab
│   │   │   └── ReviewQueue
│   │   ├── Work Cycles Tab
│   │   │   └── WorkCycles
│   │   └── Bundles Tab
│   │       └── Bundles
│   │
│   └── UserDashboard (if user)
│       ├── Tabs Navigation
│       ├── My Tasks Tab
│       │   └── MyTasks
│       └── Priority Queue Tab
│           └── PriorityQueue
│
└── Footer
```

## 🔌 API Endpoints Map

```
/auth
  POST /login          - Authenticate user
  POST /register       - Create new user

/meetings
  POST /process        - Process transcript (admin)
  GET  /               - List all meetings (admin)

/tasks
  GET  /               - All tasks (admin)
  GET  /my             - User's tasks
  GET  /queue          - Priority queue (approved)
  GET  /review         - Review queue (unapproved, admin)
  POST /               - Create task (admin)
  PATCH /{id}          - Update task
  POST /{id}/complete  - Mark complete

/workcycles
  POST /               - Create cycle (admin)
  GET  /               - List cycles
  GET  /{id}/tasks     - Cycle tasks
  GET  /{id}/snapshot  - Progress metrics

/bundles
  POST /               - Create bundle (admin)
  GET  /               - List bundles
  GET  /{id}/tasks     - Bundle tasks

/health
  GET  /               - Health check
```

## 📦 Dependencies

### Backend (Python)
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `sqlalchemy` - ORM
- `pydantic` - Data validation
- `python-multipart` - File uploads
- `google-generativeai` - Gemini AI
- `python-dotenv` - Environment variables

### Frontend (Node.js)
- `react` - UI library
- `vite` - Build tool
- Standard browser APIs (fetch, localStorage)

## 🚀 Build & Deploy

### Development
```bash
# Backend
cd backend
uvicorn main:app --reload

# Frontend
cd frontend
npm run dev
```

### Production Build
```bash
# Frontend
cd frontend
npm run build
# Output: dist/ folder

# Backend
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📝 Configuration Files

**`.env`**
```
GEMINI_API_KEY=your_api_key_here
```

**`vite.config.js`**
```javascript
export default {
  server: { port: 5173 },
  // ... other config
}
```

**`requirements.txt`**
```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
...
```

**`package.json`**
```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build"
  }
}
```

---

**This structure enables:**
- ✅ Clean separation of concerns
- ✅ Easy maintenance and updates
- ✅ Scalable architecture
- ✅ Reusable components
- ✅ Type-safe API communication
