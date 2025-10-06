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
)
from gemini_service import extract_tasks_from_transcript, generate_meeting_summary

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

def extract_tasks_from_text(db: Session, text: str, meeting_id: int) -> List[Task]:
    tasks = []
    
    # Use Gemini AI to extract tasks
    ai_tasks = extract_tasks_from_transcript(text)
    
    for task_data in ai_tasks:
        assignee_name = task_data.get("assignee", "unassigned")
        assignee = find_user_by_username(db, assignee_name)
        if not assignee:
            assignee = get_or_create_user(db, assignee_name, DEFAULT_PASSWORD, False)
        
        task = Task(
            description=task_data.get("description", "Follow up"),
            due_date=task_data.get("due_date"),
            status="To Do",
            meeting_id=meeting_id,
            assignee_id=assignee.id,
            priority=task_data.get("priority", 5),
            effort_tag=task_data.get("effort_tag"),
            confidence=task_data.get("confidence", 1.0),
            is_approved=False
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
    
    db.commit()
    db.refresh(task)
    return task


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


@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
