from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session

from backend.database import (
    init_db,
    get_db,
    get_or_create_user,
    create_token_for_user,
    User,
    Token,
    Meeting,
    Task,
)

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
    for line in text.splitlines():
        line = line.strip()
        if line.upper().startswith(TASK_PREFIX):
            payload = line[len(TASK_PREFIX):].strip()
            parts = [p.strip() for p in payload.split("|")]
            
            assignee_name = parts[0] if parts and parts[0] else "unassigned"
            description = parts[1] if len(parts) > 1 else "Follow up"
            due_date = parts[2] if len(parts) > 2 else None
            
            assignee = find_user_by_username(db, assignee_name)
            if not assignee:
                assignee = get_or_create_user(db, assignee_name, DEFAULT_PASSWORD, False)
            
            task = Task(
                description=description,
                due_date=due_date,
                status="To Do",
                meeting_id=meeting_id,
                assignee_id=assignee.id
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
    
    summary = create_summary(effective_text)
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

@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
