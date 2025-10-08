from datetime import datetime
from typing import Optional, List
import os
from dotenv import load_dotenv

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Body

load_dotenv()
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session

from database import (
    init_db,
    get_db,
    get_or_create_user,
    create_token_for_user,
    User,
    Token,
    Meeting,
    Task,
    WorkCycle,
    BundleGroup,
    ProgressSnapshot,
    Team,
    TeamMember,
    Notification,
)
from gemini_service import extract_tasks_from_transcript, generate_meeting_summary, extract_task_from_capture
from analytics_service import get_daily_briefing, get_productivity_analytics, detect_blockers_from_transcript

# Constants
DEFAULT_PASSWORD = "changeme"
TASK_PREFIX = "TASK:"
SUMMARY_MAX_LENGTH = 800
SUMMARY_PREVIEW_LENGTH = 200

# Initialize DB
init_db()

app = FastAPI(title="Meeting Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str
    
    @validator('username')
    def username_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Username cannot be empty')
        return v.strip()

class RegisterRequest(BaseModel):
    username: str
    password: str
    is_admin: bool = False
    
    @validator('username')
    def username_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Username cannot be empty')
        return v.strip()

class TaskRequest(BaseModel):
    description: str
    meeting_id: int
    assignee_username: str
    due_date: Optional[str] = None
    effort_tag: Optional[str] = None
    priority: int = 0


class TaskUpdateRequest(BaseModel):
    status: Optional[str] = None
    priority: Optional[int] = None
    effort_tag: Optional[str] = None
    bundle_id: Optional[int] = None
    workcycle_id: Optional[int] = None
    is_approved: Optional[bool] = None
    progress: Optional[int] = None
    is_blocked: Optional[bool] = None
    blocker_reason: Optional[str] = None
    story_points: Optional[int] = None
    acceptance_criteria: Optional[str] = None
    definition_of_done: Optional[str] = None

class TaskSubmissionRequest(BaseModel):
    submission_notes: str
    submission_url: Optional[str] = None

class TaskVerificationRequest(BaseModel):
    approved: bool
    verification_notes: Optional[str] = None

class TaskCaptureRequest(BaseModel):
    text: str

class TeamRequest(BaseModel):
    name: str
    description: Optional[str] = None


class WorkCycleRequest(BaseModel):
    name: str
    start_date: str
    end_date: str
    goal: Optional[str] = None


class BundleGroupRequest(BaseModel):
    title: str
    description: Optional[str] = None

class LoginResponse(BaseModel):
    token: str
    username: str
    is_admin: bool

class UserOut(BaseModel):
    id: int
    username: str
    is_admin: bool
    
    class Config:
        orm_mode = True

class MeetingOut(BaseModel):
    id: int
    title: str
    date: str
    summary_minutes: Optional[str]
    processed_by_id: Optional[int]
    
    class Config:
        orm_mode = True

class TaskOut(BaseModel):
    id: int
    description: str
    due_date: Optional[str]
    status: str
    meeting_id: int
    assignee_id: int
    priority: int = 0
    effort_tag: Optional[str] = None
    confidence: float = 1.0
    timestamp_seconds: Optional[int] = None
    is_approved: bool = False
    bundle_id: Optional[int] = None
    workcycle_id: Optional[int] = None
    progress: int = 0
    is_blocked: bool = False
    blocker_reason: Optional[str] = None
    submitted_at: Optional[str] = None
    submission_notes: Optional[str] = None
    submission_url: Optional[str] = None
    verified_at: Optional[str] = None
    verified_by_id: Optional[int] = None
    verification_notes: Optional[str] = None
    story_points: Optional[int] = None
    acceptance_criteria: Optional[str] = None
    definition_of_done: Optional[str] = None
    
    class Config:
        orm_mode = True


class WorkCycleOut(BaseModel):
    id: int
    name: str
    start_date: str
    end_date: str
    goal: Optional[str]
    owner_id: int
    
    class Config:
        orm_mode = True


class BundleGroupOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    owner_id: int
    
    class Config:
        orm_mode = True


class ProgressSnapshotOut(BaseModel):
    id: int
    workcycle_id: int
    snapshot_date: str
    remaining_effort: float
    
    class Config:
        orm_mode = True


# Auth helpers
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    
    tok = db.query(Token).filter(Token.token == token).first()
    if not tok or tok.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = db.query(User).filter(User.id == tok.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def admin_required(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

def find_user_by_username(db: Session, username: str) -> Optional[User]:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        user = db.query(User).filter(User.username.ilike(username)).first()
    return user

def create_summary(text: str) -> str:
    text = text.strip()
    if len(text) > SUMMARY_PREVIEW_LENGTH:
        return text[:SUMMARY_MAX_LENGTH] + "..."
    return text

def calculate_suggested_focus_time(due_date: Optional[str], effort_tag: Optional[str]) -> Optional[datetime]:
    if not due_date or not effort_tag:
        return None
    
    effort_hours = {"small": 1, "medium": 3, "large": 6}
    hours = effort_hours.get(effort_tag, 3)
    
    due = datetime.fromisoformat(due_date)
    suggested = due - timedelta(hours=hours)
    return suggested

def create_notification(db: Session, user_id: int, message: str, task_id: Optional[int] = None):
    notif = Notification(user_id=user_id, message=message, task_id=task_id)
    db.add(notif)
    db.commit()

def check_approval_workflow(task: Task) -> str:
    if task.story_points and task.story_points > 8:
        return "Manager Approval Pending"
    if task.effort_tag == "large":
        return "Manager Approval Pending"
    return "To Do"

def extract_tasks_from_text(db: Session, text: str, meeting_id: int) -> List[Task]:
    tasks = []
    ai_tasks = extract_tasks_from_transcript(text)
    
    for task_data in ai_tasks:
        assignee_name = task_data.get("assignee", "unassigned")
        assignee = find_user_by_username(db, assignee_name)
        if not assignee:
            assignee = get_or_create_user(db, assignee_name, DEFAULT_PASSWORD, False)
        
        confidence = task_data.get("confidence", 1.0)
        priority = task_data.get("priority", 5)
        needs_review = False
        
        if confidence < 0.7:
            priority = 4
            needs_review = True
        
        task = Task(
            description=task_data.get("description", "Follow up"),
            due_date=task_data.get("due_date"),
            status="To Do",
            meeting_id=meeting_id,
            assignee_id=assignee.id,
            priority=priority,
            effort_tag=task_data.get("effort_tag"),
            confidence=confidence,
            is_approved=False,
            is_potential_risk=task_data.get("is_potential_risk", False),
            risk_reason=task_data.get("risk_reason"),
            needs_priority_review=needs_review,
            suggested_focus_time=calculate_suggested_focus_time(task_data.get("due_date"), task_data.get("effort_tag"))
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        tasks.append(task)
    
    return tasks


# Auth endpoints
@app.post("/auth/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = find_user_by_username(db, request.username)
    if not user or user.password != request.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token_str = create_token_for_user(db, user)
    return LoginResponse(
        token=token_str,
        username=user.username,
        is_admin=user.is_admin
    )

@app.post("/auth/register", response_model=UserOut)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == request.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    user = get_or_create_user(db, request.username, request.password, request.is_admin)
    return user


@app.post("/meetings/process", response_model=MeetingOut, status_code=201)
async def process_meeting(
    title: str = Form(...),
    date: Optional[str] = Form(None),
    transcript: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db),
):
    if not transcript and not file:
        raise HTTPException(status_code=400, detail="Provide transcript or audio file")
    
    effective_text = transcript or ""
    if file and not transcript:
        try:
            await file.read()
            effective_text = f"[Audio uploaded: {file.filename} — transcription not enabled]"
        except Exception:
            effective_text = "[Audio uploaded — processing failed]"
    
    summary = generate_meeting_summary(effective_text) if effective_text else "No summary"
    meeting_date = date or datetime.utcnow().isoformat()
    
    meeting = Meeting(
        title=title,
        date=meeting_date,
        summary_minutes=summary,
        processed_by_id=current_user.id
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    
    if effective_text:
        extract_tasks_from_text(db, effective_text, meeting.id)
    
    return meeting


@app.get("/meetings", response_model=List[MeetingOut])
def list_meetings(current_user: User = Depends(admin_required), db: Session = Depends(get_db)):
    return db.query(Meeting).order_by(Meeting.created_at.desc()).all()

@app.get("/tasks", response_model=List[TaskOut])
def list_tasks(current_user: User = Depends(admin_required), db: Session = Depends(get_db)):
    return db.query(Task).order_by(Task.created_at.desc()).all()

@app.get("/tasks/my", response_model=List[TaskOut])
def my_tasks(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Task).filter(Task.assignee_id == current_user.id).order_by(Task.created_at.desc()).all()

@app.post("/tasks", response_model=TaskOut, status_code=201)
def create_task(
    request: TaskRequest,
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db),
):
    meeting = db.query(Meeting).filter(Meeting.id == request.meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    assignee = find_user_by_username(db, request.assignee_username)
    if not assignee:
        assignee = get_or_create_user(db, request.assignee_username, DEFAULT_PASSWORD, False)
    
    task = Task(
        description=request.description,
        due_date=request.due_date,
        status="To Do",
        meeting_id=meeting.id,
        assignee_id=assignee.id
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@app.post("/tasks/{task_id}/complete", response_model=TaskOut)
def complete_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.assignee_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    
    task.status = "Done"
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

# Priority Queue endpoints
@app.get("/tasks/queue", response_model=List[TaskOut])
def priority_queue(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Task).filter(Task.is_approved == True, Task.workcycle_id == None).order_by(Task.priority.desc(), Task.created_at.desc()).all()


@app.get("/tasks/review", response_model=List[TaskOut])
def review_queue(current_user: User = Depends(admin_required), db: Session = Depends(get_db)):
    return db.query(Task).filter(Task.is_approved == False).order_by(Task.confidence.desc(), Task.created_at.desc()).all()


@app.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, request: TaskUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if request.status is not None:
        task.status = request.status
    if request.priority is not None:
        task.priority = request.priority
    if request.effort_tag is not None:
        task.effort_tag = request.effort_tag
    if request.bundle_id is not None:
        task.bundle_id = request.bundle_id
    if request.workcycle_id is not None:
        task.workcycle_id = request.workcycle_id
    if request.is_approved is not None:
        task.is_approved = request.is_approved
    if request.progress is not None:
        task.progress = request.progress
        if request.progress == 100:
            task.status = "Done"
    if request.is_blocked is not None:
        task.is_blocked = request.is_blocked
    if request.blocker_reason is not None:
        task.blocker_reason = request.blocker_reason
    if request.story_points is not None:
        task.story_points = request.story_points
    if request.acceptance_criteria is not None:
        task.acceptance_criteria = request.acceptance_criteria
    if request.definition_of_done is not None:
        task.definition_of_done = request.definition_of_done
    
    db.commit()
    db.refresh(task)
    return task

@app.post("/tasks/{task_id}/submit", response_model=TaskOut)
def submit_task(task_id: int, request: TaskSubmissionRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.assignee_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only assignee can submit")
    
    task.submitted_at = datetime.utcnow()
    task.submission_notes = request.submission_notes
    task.submission_url = request.submission_url
    task.status = "Submitted"
    task.progress = 100
    task.verification_deadline_at = datetime.utcnow() + timedelta(hours=24)
    
    create_notification(db, task.assignee_id, f"Task submitted for review: {task.description}", task.id)
    
    db.commit()
    db.refresh(task)
    return task

@app.post("/tasks/{task_id}/verify", response_model=TaskOut)
def verify_task(task_id: int, request: TaskVerificationRequest, current_user: User = Depends(admin_required), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if not task.submitted_at:
        raise HTTPException(status_code=400, detail="Task not submitted yet")
    
    task.verified_at = datetime.utcnow()
    task.verified_by_id = current_user.id
    task.verification_notes = request.verification_notes
    
    if request.approved:
        task.status = "Done"
        create_notification(db, task.assignee_id, f"Task approved: {task.description}", task.id)
    else:
        task.status = "Doing"
        task.submitted_at = None
        task.progress = 50
        create_notification(db, task.assignee_id, f"Task rejected: {task.description}. Feedback: {request.verification_notes}", task.id)
    
    db.commit()
    db.refresh(task)
    return task

@app.get("/tasks/pending-verification", response_model=List[TaskOut])
def pending_verification(current_user: User = Depends(admin_required), db: Session = Depends(get_db)):
    return db.query(Task).filter(Task.status == "Submitted", Task.verified_at == None).order_by(Task.submitted_at.desc()).all()


# Work Cycle endpoints
@app.post("/workcycles", response_model=WorkCycleOut, status_code=201)
def create_workcycle(request: WorkCycleRequest, current_user: User = Depends(admin_required), db: Session = Depends(get_db)):
    cycle = WorkCycle(
        name=request.name,
        start_date=request.start_date,
        end_date=request.end_date,
        goal=request.goal,
        owner_id=current_user.id
    )
    db.add(cycle)
    db.commit()
    db.refresh(cycle)
    return cycle


@app.get("/workcycles", response_model=List[WorkCycleOut])
def list_workcycles(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(WorkCycle).order_by(WorkCycle.created_at.desc()).all()


@app.get("/workcycles/{cycle_id}/tasks", response_model=List[TaskOut])
def workcycle_tasks(cycle_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Task).filter(Task.workcycle_id == cycle_id).order_by(Task.priority.desc()).all()


@app.get("/workcycles/{cycle_id}/snapshot")
def workcycle_snapshot(cycle_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cycle = db.query(WorkCycle).filter(WorkCycle.id == cycle_id).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="Work cycle not found")
    
    tasks = db.query(Task).filter(Task.workcycle_id == cycle_id).all()
    
    effort_map = {"small": 1, "medium": 3, "large": 5}
    total_effort = sum(effort_map.get(t.effort_tag, 0) for t in tasks)
    remaining_effort = sum(effort_map.get(t.effort_tag, 0) for t in tasks if t.status != "Done")
    
    blockers = [t for t in tasks if "block" in t.description.lower() or "stuck" in t.description.lower()]
    doing = [t for t in tasks if t.status == "Doing"]
    upcoming = [t for t in tasks if t.due_date and t.status not in ["Done", "Doing"]]
    
    return {
        "cycle_name": cycle.name,
        "total_items": len(tasks),
        "completed_items": len([t for t in tasks if t.status == "Done"]),
        "total_effort": total_effort,
        "remaining_effort": remaining_effort,
        "blockers": [{"id": t.id, "description": t.description} for t in blockers[:3]],
        "doing": [{"id": t.id, "description": t.description} for t in doing[:3]],
        "upcoming": [{"id": t.id, "due_date": t.due_date} for t in upcoming[:3]]
    }


# Bundle Group endpoints
@app.post("/bundles", response_model=BundleGroupOut, status_code=201)
def create_bundle(request: BundleGroupRequest, current_user: User = Depends(admin_required), db: Session = Depends(get_db)):
    bundle = BundleGroup(
        title=request.title,
        description=request.description,
        owner_id=current_user.id
    )
    db.add(bundle)
    db.commit()
    db.refresh(bundle)
    return bundle


@app.get("/bundles", response_model=List[BundleGroupOut])
def list_bundles(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(BundleGroup).order_by(BundleGroup.created_at.desc()).all()


@app.get("/bundles/{bundle_id}/tasks", response_model=List[TaskOut])
def bundle_tasks(bundle_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Task).filter(Task.bundle_id == bundle_id).all()


@app.get("/analytics/briefing")
def daily_briefing(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_daily_briefing(db)

@app.get("/analytics/productivity")
def productivity_analytics(days: int = 7, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_productivity_analytics(db, days)

@app.post("/tasks/capture", response_model=TaskOut, status_code=201)
def capture_task(request: TaskCaptureRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    extracted = extract_task_from_capture(request.text)
    
    assignee_name = extracted.get("assignee", "unassigned")
    assignee = find_user_by_username(db, assignee_name)
    if not assignee:
        assignee = current_user
    
    meeting = db.query(Meeting).first()
    if not meeting:
        meeting = Meeting(title="Quick Capture", date=datetime.utcnow().isoformat(), processed_by_id=current_user.id)
        db.add(meeting)
        db.commit()
        db.refresh(meeting)
    
    task = Task(
        description=extracted.get("description", request.text[:200]),
        status="Capture Inbox",
        meeting_id=meeting.id,
        assignee_id=assignee.id,
        priority=5,
        is_approved=False
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@app.post("/tasks/{task_id}/approve-manager", response_model=TaskOut)
def approve_manager(task_id: int, current_user: User = Depends(admin_required), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status != "Manager Approval Pending":
        raise HTTPException(status_code=400, detail="Task not pending approval")
    
    task.status = "To Do"
    task.is_approved = True
    create_notification(db, task.assignee_id, f"Task approved by manager: {task.description}", task.id)
    
    db.commit()
    db.refresh(task)
    return task

@app.get("/tasks/sla-breached", response_model=List[TaskOut])
def sla_breached_tasks(current_user: User = Depends(admin_required), db: Session = Depends(get_db)):
    now = datetime.utcnow()
    tasks = db.query(Task).filter(
        Task.status == "Submitted",
        Task.verification_deadline_at < now,
        Task.verified_at == None
    ).all()
    
    for task in tasks:
        if not task.sla_breached:
            task.sla_breached = True
            create_notification(db, task.assignee_id, f"SLA breach: Task verification overdue - {task.description}", task.id)
    
    db.commit()
    return tasks

@app.post("/teams", status_code=201)
def create_team(request: TeamRequest, current_user: User = Depends(admin_required), db: Session = Depends(get_db)):
    team = Team(name=request.name, description=request.description)
    db.add(team)
    db.commit()
    db.refresh(team)
    return team

@app.post("/teams/{team_id}/members/{user_id}")
def add_team_member(team_id: int, user_id: int, current_user: User = Depends(admin_required), db: Session = Depends(get_db)):
    member = TeamMember(team_id=team_id, user_id=user_id)
    db.add(member)
    db.commit()
    return {"status": "added"}

@app.get("/notifications")
def get_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).limit(50).all()

@app.patch("/notifications/{notif_id}/read")
def mark_notification_read(notif_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(Notification.id == notif_id, Notification.user_id == current_user.id).first()
    if notif:
        notif.is_read = True
        db.commit()
    return {"status": "read"}

@app.post("/tasks/plan-tomorrow")
def plan_tomorrow(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tasks = db.query(Task).filter(
        Task.assignee_id == current_user.id,
        Task.status.in_(["To Do", "Doing"]),
        Task.progress < 100
    ).all()
    
    tomorrow = (datetime.utcnow() + timedelta(days=1)).date().isoformat()
    
    for task in tasks:
        task.status = "Planned for Tomorrow"
        if not task.due_date or task.due_date < tomorrow:
            task.due_date = tomorrow
    
    db.commit()
    return {"count": len(tasks), "status": "planned"}

@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
