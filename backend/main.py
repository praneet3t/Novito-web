# backend/main.py
import os
import json
import base64
import re
from datetime import datetime, timedelta
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
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Importing from package-qualified path to avoid ModuleNotFoundError when running uvicorn from project root.
from backend.database import (
    SessionLocal,
    init_db,
    get_db,
    get_or_create_user,
    User,
    Meeting,
    Task,
)

# AI SDK import (Gemini via google-generativeai)
try:
    import google.generativeai as genai  # type: ignore
except Exception:
    genai = None  # type: ignore

# JWT
import jwt

# Initialize DB (no-op if already initialized)
init_db()

# Config
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
JWT_SECRET = os.getenv("MEETING_AGENT_JWT_SECRET", "change-this-secret")
JWT_ALGO = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # one week

# Configure genai if available
if genai is not None:
    try:
        if hasattr(genai, "configure"):
            genai.configure(api_key=GEMINI_API_KEY)
    except Exception:
        pass

app = FastAPI(title="Meeting Agent - Backend")


# OAuth2 token scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# Simple JWT utilities
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGO)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token decode error")
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def admin_required(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user


# Pydantic schemas
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    username: str
    password: str
    is_admin: Optional[bool] = False


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


# Auth endpoints
@app.post("/auth/register", response_model=UserOut)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(username=data.username, password=data.password, is_admin=bool(data.is_admin))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/auth/login", response_model=TokenResponse)
def login(form_data: dict = Body(...), db: Session = Depends(get_db)):
    """
    Expects JSON body: {"username": "...", "password": "..."}
    Returns JWT token on success.
    """
    username = form_data.get("username")
    password = form_data.get("password")
    if not username or not password:
        raise HTTPException(status_code=400, detail="username and password required")
    user = db.query(User).filter(User.username == username).first()
    if not user or user.password != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


# Helper: call Gemini model to analyze meeting text and extract JSON tasks
def call_gemini_for_meeting(meeting_title: str, meeting_text: str) -> dict:
    """
    Ask the Gemini model to produce a JSON with:
    {
      "summary": "<concise summary>",
      "tasks": [
        {"description": "...", "assignee": "<username or name or 'unassigned'>", "due_date": "YYYY-MM-DD" (optional)}
      ]
    }
    """
    if genai is None:
        raise RuntimeError("google.generativeai (genai) SDK is not installed or importable")

    prompt = (
        f"You are an assistant that extracts meeting minutes and action items.\n\n"
        f"Meeting Title: {meeting_title}\n\n"
        f"Meeting Transcript/Text:\n{meeting_text}\n\n"
        "Produce a JSON object ONLY (no surrounding text) with two keys: \"summary\" and \"tasks\".\n"
        "- \"summary\" should be a concise minutes-of-meeting paragraph (3-6 sentences).\n"
        "- \"tasks\" should be an array of objects. Each task object must have: \"description\" (string), "
        "\"assignee\" (string; username or name or 'unassigned'), and optional \"due_date\" (ISO date YYYY-MM-DD) if obvious.\n"
        "Ensure the output is valid JSON. If there are no tasks, return an empty array for \"tasks\".\n"
        "Example output:\n"
        r'{"summary":"...","tasks":[{"description":"...","assignee":"alice","due_date":"2025-10-15"}]}' "\n\n"
        "Now analyze and output the JSON."
    )

    try:
        # Try different API styles depending on SDK version
        # Preferred: model.generate_content
        if hasattr(genai, "GenerativeModel"):
            model = genai.GenerativeModel("gemini-1.5-flash")
            resp = model.generate_content(contents=prompt)
            text_out = getattr(resp, "text", None) or str(resp)
        else:
            # Fallback to client
            client = genai.Client()
            resp = client.generate_text(model="gemini-1.5-flash", prompt=prompt)
            text_out = getattr(resp, "text", None) or str(resp)
    except Exception as e:
        raise RuntimeError(f"AI generation error: {e}")

    # Extract JSON substring from text_out
    try:
        match = re.search(r"(\{[\s\S]*\})", text_out)
        json_text = match.group(1) if match else text_out.strip()
        parsed = json.loads(json_text)
        return parsed
    except Exception:
        # Try to clean and parse manually
        cleaned = text_out.strip()
        first = cleaned.find("{")
        last = cleaned.rfind("}")
        if first != -1 and last != -1 and last > first:
            cleaned = cleaned[first:last+1]
            try:
                parsed = json.loads(cleaned)
                return parsed
            except Exception as e:
                raise RuntimeError("Failed to parse JSON from model output. Raw output snippet: " + repr(text_out)[:300]) from e
        raise RuntimeError("Failed to parse JSON from model output. Raw output snippet: " + repr(text_out)[:300])


# Endpoint: Admin processes meeting (upload audio OR provide transcript)
@app.post("/meetings/process", response_model=MeetingOut, status_code=201)
async def process_meeting(
    title: str = Form(...),
    date: Optional[str] = Form(None),
    transcript: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db),
):
    """
    Admin-only. Accepts:
    - title (form)
    - date (optional ISO string) (form)
    - transcript (optional text) (form)
    - file (optional audio file) (multipart file)
    At least one of transcript or file must be provided.
    """
    if not transcript and not file:
        raise HTTPException(status_code=400, detail="Provide transcript text or upload an audio file")

    effective_text = transcript
    if file and not transcript:
        file_bytes = await file.read()
        b64 = base64.b64encode(file_bytes).decode("utf-8")
        transcript_prompt = (
            "You are an assistant that transcribes audio. The audio file is base64-encoded below.\n\n"
            "Decode and transcribe the audio to plain text. Only output the transcript text (no metadata).\n\n"
            "AUDIO_BASE64:\n" + b64
        )
        try:
            if genai is None:
                raise RuntimeError("Server not configured with google.generativeai SDK; cannot transcribe audio.")
            if hasattr(genai, "GenerativeModel"):
                model = genai.GenerativeModel("gemini-1.5-flash")
                resp = model.generate_content(contents=transcript_prompt)
                text_out = getattr(resp, "text", None) or str(resp)
            else:
                client = genai.Client()
                resp = client.generate_text(model="gemini-1.5-flash", prompt=transcript_prompt)
                text_out = getattr(resp, "text", None) or str(resp)
            effective_text = text_out.strip()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Audio transcription failed: {e}")

    if not effective_text or effective_text.strip() == "":
        raise HTTPException(status_code=400, detail="No transcript text available after processing")

    try:
        parsed = call_gemini_for_meeting(title, effective_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {e}")

    summary = parsed.get("summary", None)
    tasks_list = parsed.get("tasks", []) or []

    meeting_date = date or datetime.utcnow().isoformat()
    meeting = Meeting(title=title, date=meeting_date, summary_minutes=summary, processed_by_id=current_user.id)
    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    created_tasks = []
    for t in tasks_list:
        desc = t.get("description") if isinstance(t, dict) else None
        assignee = t.get("assignee") if isinstance(t, dict) else None
        due = t.get("due_date") if isinstance(t, dict) else None
        if not desc:
            continue
        assignee_name = (assignee or "unassigned").strip()
        if assignee_name.lower() == "unassigned" or assignee_name == "":
            assignee_user = db.query(User).filter(User.username == "unassigned").first()
            if not assignee_user:
                assignee_user = User(username="unassigned", password="unassigned123", is_admin=False)
                db.add(assignee_user)
                db.commit()
                db.refresh(assignee_user)
        else:
            assignee_user = db.query(User).filter(User.username == assignee_name).first()
            if not assignee_user:
                assignee_user = User(username=assignee_name, password="changeme", is_admin=False)
                db.add(assignee_user)
                db.commit()
                db.refresh(assignee_user)
        due_dt = None
        if due:
            due_dt = due
        new_task = Task(description=desc, due_date=due_dt, status="To Do", meeting_id=meeting.id, assignee_id=assignee_user.id)
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        created_tasks.append(new_task)

    db.refresh(meeting)
    return meeting


# Admin: list all meetings
@app.get("/meetings", response_model=List[MeetingOut])
def list_meetings(current_user: User = Depends(admin_required), db: Session = Depends(get_db)):
    meetings = db.query(Meeting).order_by(Meeting.date.desc()).all()
    return meetings


# User: list their assigned tasks
@app.get("/tasks/my", response_model=List[TaskOut])
def my_tasks(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tasks = db.query(Task).filter(Task.assignee_id == current_user.id).order_by(Task.id.desc()).all()
    return tasks


# Admin: list all tasks
@app.get("/tasks", response_model=List[TaskOut])
def list_tasks(current_user: User = Depends(admin_required), db: Session = Depends(get_db)):
    tasks = db.query(Task).order_by(Task.id.desc()).all()
    return tasks


# Update task completion (user or admin)
@app.post("/tasks/{task_id}/complete", response_model=TaskOut)
def complete_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.assignee_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not allowed to update this task")
    task.status = "Done"
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


# Admin: create a task manually and assign
@app.post("/tasks", response_model=TaskOut, status_code=201)
def create_task_manual(
    description: str = Body(..., embed=True),
    meeting_id: int = Body(..., embed=True),
    assignee_username: str = Body(..., embed=True),
    due_date: Optional[str] = Body(None, embed=True),
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db),
):
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    assignee = db.query(User).filter(User.username == assignee_username).first()
    if not assignee:
        assignee = User(username=assignee_username, password="changeme", is_admin=False)
        db.add(assignee)
        db.commit()
        db.refresh(assignee)
    new_task = Task(
        description=description,
        due_date=due_date,
        status="To Do",
        meeting_id=meeting.id,
        assignee_id=assignee.id,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


# Basic health
@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}


# Simple utility endpoint to list users (admin)
@app.get("/users", response_model=List[UserOut])
def list_users(current_user: User = Depends(admin_required), db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.username.asc()).all()
    return users
