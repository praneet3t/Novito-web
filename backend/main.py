# backend/main.py
import os
import json
import re
from datetime import datetime
from typing import Optional, List

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
    Form,
    Body,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
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

# Initialize DB
init_db()

app = FastAPI(title="Meeting Agent - Simple Auth Demo")

# CORS - permissive for local development/demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 helper to extract Bearer token string
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# Pydantic response models
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


# Auth helpers (token stored in DB)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    tok = db.query(Token).filter(Token.token == token).first()
    if not tok:
        raise HTTPException(status_code=401, detail="Invalid token")
    if tok.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Token expired")
    user = db.query(User).filter(User.id == tok.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def admin_required(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin required")
    return current_user


# Auth endpoints
@app.post("/auth/login", response_model=LoginResponse)
def login(form_data: dict = Body(...), db: Session = Depends(get_db)):
    """
    Expects JSON: {"username":"...","password":"..."}
    Returns: {"token":"...","username":"...","is_admin":bool}
    """
    username = (form_data.get("username") or "").strip()
    password = form_data.get("password") or ""
    if not username or not password:
        raise HTTPException(status_code=400, detail="username and password required")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        # try case-insensitive
        user = db.query(User).filter(User.username.ilike(username)).first()
    if not user or user.password != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token_str = create_token_for_user(db, user)
    return {"token": token_str, "username": user.username, "is_admin": user.is_admin}


@app.post("/auth/register", response_model=UserOut)
def register(data: dict = Body(...), db: Session = Depends(get_db)):
    uname = (data.get("username") or "").strip()
    pwd = data.get("password") or ""
    is_admin = bool(data.get("is_admin", False))
    if not uname or not pwd:
        raise HTTPException(status_code=400, detail="username and password required")
    existing = db.query(User).filter(User.username == uname).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username exists")
    user = get_or_create_user(db, uname, pwd, is_admin)
    return user


# Demo debug: list users and passwords (only for local debugging)
@app.get("/debug/users")
def debug_users(db: Session = Depends(get_db)):
    rows = db.query(User).order_by(User.username.asc()).all()
    return [{"username": u.username, "password": u.password, "is_admin": u.is_admin} for u in rows]


# Meetings processing (simple demo - no AI)
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
            _ = await file.read()
            effective_text = f"[Audio uploaded: {file.filename} — transcription not enabled in demo]"
        except Exception:
            effective_text = "[Audio uploaded — unreadable]"

    summary = (effective_text.strip()[:800] + "...") if len(effective_text.strip()) > 200 else effective_text.strip()
    meeting_date = date or datetime.utcnow().isoformat()
    meeting = Meeting(title=title, date=meeting_date, summary_minutes=summary, processed_by_id=current_user.id)
    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    # simple task extraction demo: lines that start with "TASK:" formatted as TASK:assignee|description|due(optional)
    created = []
    if effective_text:
        for line in effective_text.splitlines():
            line = line.strip()
            if line.upper().startswith("TASK:"):
                payload = line[5:].strip()
                parts = [p.strip() for p in payload.split("|")]
                assignee_name = parts[0] if len(parts) >= 1 and parts[0] else "unassigned"
                desc = parts[1] if len(parts) >= 2 else "Follow up"
                due = parts[2] if len(parts) >= 3 else None
                assignee = db.query(User).filter(User.username == assignee_name).first()
                if not assignee:
                    assignee = get_or_create_user(db, assignee_name, "changeme", False)
                task = Task(description=desc, due_date=due, status="To Do", meeting_id=meeting.id, assignee_id=assignee.id)
                db.add(task)
                db.commit()
                db.refresh(task)
                created.append(task)

    db.refresh(meeting)
    return meeting


# List meetings (admin)
@app.get("/meetings", response_model=List[MeetingOut])
def list_meetings(current_user: User = Depends(admin_required), db: Session = Depends(get_db)):
    meetings = db.query(Meeting).order_by(Meeting.created_at.desc()).all()
    return meetings


# Tasks endpoints
@app.get("/tasks", response_model=List[TaskOut])
def list_tasks(current_user: User = Depends(admin_required), db: Session = Depends(get_db)):
    tasks = db.query(Task).order_by(Task.created_at.desc()).all()
    return tasks


@app.get("/tasks/my", response_model=List[TaskOut])
def my_tasks(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tasks = db.query(Task).filter(Task.assignee_id == current_user.id).order_by(Task.created_at.desc()).all()
    return tasks


@app.post("/tasks", response_model=TaskOut, status_code=201)
def create_task_manual(
    body: dict = Body(...),
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db),
):
    desc = body.get("description")
    meeting_id = body.get("meeting_id")
    assignee_username = body.get("assignee_username")
    due_date = body.get("due_date")
    if not desc or not meeting_id or not assignee_username:
        raise HTTPException(status_code=400, detail="description, meeting_id and assignee_username required")
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    assignee = db.query(User).filter(User.username == assignee_username).first()
    if not assignee:
        assignee = get_or_create_user(db, assignee_username, "changeme", False)
    task = Task(description=desc, due_date=due_date, status="To Do", meeting_id=meeting.id, assignee_id=assignee.id)
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
        raise HTTPException(status_code=403, detail="Cannot modify this task")
    task.status = "Done"
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


# Health
@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}
