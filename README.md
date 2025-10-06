# 🤖 Meeting Agent - AI-Powered Task Management

An intelligent meeting assistant that automatically extracts action items from meeting transcripts using Google Gemini AI and manages them through an agile workflow.

## ✨ Features

### 🎯 Core Capabilities
- **AI Task Extraction**: Automatically identifies tasks, assignees, deadlines, and priorities from meeting transcripts using Gemini 2.0 Flash
- **Smart Summarization**: Generates concise meeting summaries highlighting key decisions
- **Agile Workflow**: Review queue, priority management, effort estimation (small/medium/large)
- **Work Cycles**: Sprint-like cycles with progress tracking and burndown metrics
- **Bundle Groups**: Organize related tasks into logical bundles
- **Role-Based Access**: Admin and user roles with different permissions

### 👥 User Roles

**Admin**
- Process meeting transcripts and audio files
- Review and approve AI-extracted tasks
- Adjust task priorities and effort estimates
- Create work cycles and bundles
- View all tasks and meetings

**User**
- View assigned tasks
- Mark tasks as complete
- Access priority queue of approved tasks
- Track personal workload

## 🏗️ Architecture

```
Novito-web/
├── backend/
│   ├── main.py              # FastAPI application & endpoints
│   ├── database.py          # SQLAlchemy models & DB setup
│   ├── gemini_service.py    # AI task extraction service
│   ├── seed_data.py         # Example data generator
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page-level components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── utils/           # API utilities
│   │   ├── App.jsx          # Main app component
│   │   └── App.css          # Professional dark theme
│   └── package.json
└── .env                     # Environment variables
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- Google Gemini API key

### Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set environment variable (or use .env file)
# GEMINI_API_KEY=your_api_key_here

# Seed example data
python -c "from seed_data import seed_example_data; seed_example_data()"

# Run server
uvicorn main:app --reload
```

Backend runs at: `http://127.0.0.1:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend runs at: `http://localhost:5173`

## 📊 Example Data

The system comes pre-seeded with realistic examples:

### Demo Accounts
- **Admin**: `Admin` / `admin123` (Full access)
- **Users**: 
  - `Priya` / `priya123`
  - `Arjun` / `arjun456`
  - `Raghav` / `raghav789`

### Sample Meetings
1. **Q1 Planning Meeting** - Contains tasks for authentication module
2. **Sprint Retrospective** - Contains optimization and deployment tasks

### Sample Work Cycle
- **Q1 Sprint 1** - 14-day sprint with authentication goals
- Tracks 7 tasks with varying priorities and effort levels

### Sample Bundle
- **Authentication Feature** - Groups all auth-related tasks

### Sample Tasks
- OAuth2 implementation (Priya, Priority 9, Large)
- API endpoint design (Arjun, Priority 8, Medium)
- Unit testing (Raghav, Priority 7, Medium)
- Documentation updates (Priya, Priority 6, Small)
- Database optimization (Arjun, Priority 8, Medium)
- CI/CD setup (Raghav, Priority 9, Large)
- Code review (Admin, Priority 10, Small)

## 🎯 Usage Workflow

### 1. Process Meeting (Admin)
```
1. Navigate to "Overview" tab
2. Enter meeting title and date
3. Paste transcript or upload audio
4. Click "Process"
5. AI extracts tasks automatically
```

**Example Transcript:**
```
Priya: I'll handle the OAuth2 implementation by next Friday.
Arjun: I can design the API endpoints, should take about 3 days.
Raghav: I'll write the unit tests after Priya's done, probably need a week.
Admin: Everyone, let's prioritize the code review - it's blocking deployment.
```

**AI Output:**
- Task 1: "Implement OAuth2 login flow" → Priya, Priority 9, Large, Due: Next Friday
- Task 2: "Design user profile API endpoints" → Arjun, Priority 8, Medium, Due: 3 days
- Task 3: "Write unit tests for authentication" → Raghav, Priority 7, Medium, Due: 1 week
- Task 4: "Review and merge authentication PR" → Admin, Priority 10, Small, Urgent

### 2. Review Queue (Admin)
```
1. Go to "Review Queue" tab
2. Review AI-extracted tasks
3. Adjust priority (1-10) and effort (small/medium/large)
4. Click "Approve" to add to priority queue
```

### 3. Work Cycles (Admin)
```
1. Go to "Work Cycles" tab
2. Create new cycle with name, dates, and goal
3. Assign approved tasks to cycle
4. View snapshot for progress metrics
```

### 4. Priority Queue (Users)
```
1. Go to "Priority Queue" tab
2. View approved tasks sorted by priority
3. Pick next task based on priority and effort
```

### 5. My Tasks (Users)
```
1. Go to "My Tasks" tab
2. View all assigned tasks
3. Click "Mark Done" when complete
```

## 🔌 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - Create new user

### Meetings
- `POST /meetings/process` - Process transcript/audio
- `GET /meetings` - List all meetings

### Tasks
- `GET /tasks` - All tasks (admin)
- `GET /tasks/my` - User's tasks
- `GET /tasks/queue` - Priority queue (approved)
- `GET /tasks/review` - Review queue (unapproved)
- `POST /tasks` - Create manual task
- `PATCH /tasks/{id}` - Update task
- `POST /tasks/{id}/complete` - Mark complete

### Work Cycles
- `POST /workcycles` - Create cycle
- `GET /workcycles` - List cycles
- `GET /workcycles/{id}/tasks` - Cycle tasks
- `GET /workcycles/{id}/snapshot` - Progress snapshot

### Bundles
- `POST /bundles` - Create bundle
- `GET /bundles` - List bundles
- `GET /bundles/{id}/tasks` - Bundle tasks

## 🤖 AI Integration

### Gemini 2.0 Flash Features
- **Task Extraction**: Identifies action items with context
- **Assignee Detection**: Recognizes who committed to what
- **Priority Inference**: Estimates urgency from language cues
- **Effort Estimation**: Categorizes task complexity
- **Confidence Scoring**: Rates extraction certainty (0.0-1.0)
- **Smart Summarization**: Distills key meeting outcomes

### Prompt Engineering
The system uses structured prompts to ensure consistent JSON output:
```python
{
  "assignee": "Name",
  "description": "Clear task description",
  "due_date": "2024-01-15",
  "priority": 5,
  "effort_tag": "medium",
  "confidence": 0.9
}
```

## 🎨 UI Features

### Professional Dark Theme
- Modern gradient branding
- Smooth animations and transitions
- Responsive grid layouts
- Color-coded badges (effort levels)
- Stat cards for metrics
- Hover effects and focus states

### Component Structure
- **Pages**: LoginPage, AdminDashboard, UserDashboard
- **Components**: ProcessMeeting, ReviewQueue, WorkCycles, Bundles, PriorityQueue, MyTasks
- **Hooks**: useAuth for authentication state
- **Utils**: Centralized API client

## 🔒 Security Notes

⚠️ **This is a demo application**
- Passwords stored in plain text
- No encryption on tokens
- CORS allows all origins
- Not production-ready

For production:
- Use bcrypt for password hashing
- Implement JWT with proper expiration
- Add HTTPS/TLS
- Restrict CORS origins
- Add rate limiting
- Implement proper session management

## 📈 Future Enhancements

- [ ] Audio transcription (Whisper API)
- [ ] Real-time collaboration (WebSockets)
- [ ] Email notifications
- [ ] Calendar integration
- [ ] Burndown charts
- [ ] Task dependencies
- [ ] Time tracking
- [ ] Export reports (PDF/CSV)
- [ ] Mobile app
- [ ] Slack/Teams integration

## 🐛 Troubleshooting

**Backend won't start:**
```bash
# Check Python version
python --version  # Should be 3.9+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Frontend won't start:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**AI not extracting tasks:**
- Verify GEMINI_API_KEY in .env
- Check API quota at https://makersuite.google.com/
- Review backend logs for errors

**Database issues:**
```bash
# Delete and recreate
rm meeting_agent.db
python -c "from database import init_db; init_db()"
python -c "from seed_data import seed_example_data; seed_example_data()"
```

## 📝 License

MIT License - Feel free to use for learning and projects

## 🙏 Credits

- **AI**: Google Gemini 2.0 Flash
- **Backend**: FastAPI, SQLAlchemy
- **Frontend**: React, Vite
- **Design**: Inter font, Custom dark theme

---

**Built with ❤️ for smarter meetings and better task management**
