import json
import os
import shutil
import tempfile
from typing import Dict, List, Optional

import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import (FastAPI, Depends, File, Form, HTTPException, Request,
                     UploadFile, status)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

# Use a relative import that works from the root directory
from .database import User, Task, Meeting, get_db, get_or_create_user

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

app = FastAPI(title="Meeting Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# --- Pydantic Schemas ---

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    is_admin: bool

class AssigneeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: str

class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    description: str
    due_date: Optional[str] = None
    status: str
    assignee: AssigneeOut
    meeting_id: int

class MeetingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    date: str
    summary_minutes: Optional[str] = ""

class TaskUpdate(BaseModel):
    status: str

class ProcessResult(BaseModel):
    meeting_id: int
    created_tasks: int

class AdminDashboardStats(BaseModel):
    total_meetings: int
    total_tasks: int
    tasks_todo: int
    tasks_completed: int

# --- Authentication ---

async def auth_dependency(request: Request, db: Session = Depends(get_db)) -> User:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth header format")
    
    username = parts[1]
    user = db.query(User).filter(User.username.ilike(username)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return user
    
async def admin_dependency(current_user: User = Depends(auth_dependency)) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required.")
    return current_user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or user.password != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    return Token(access_token=user.username)


# --- Gemini AI Integration ---

def _get_gemini_prompt() -> str:
    return (
        "You are an expert assistant that extracts a concise Minutes of Meeting and all action items from a meeting transcript. "
        "Return STRICT JSON with two keys: 'minutes' (string) and 'tasks' (array). "
        "Each object in the 'tasks' array must have these keys: "
        "'description' (string), 'assignee' (string, just the person's first name), and 'due_date' (optional string). "
        "Do not include any commentary or prose outside of the main JSON object."
    )

def _parse_gemini_response(response_text: str) -> Dict:
    text = response_text.strip()
    if text.startswith("```") and text.endswith("```"):
        text = text.strip("`\n ")
        if text.lower().startswith("json"):
            text = text[4:].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="AI response was not valid JSON.")


# --- Core Logic ---

def _process_and_save(extracted_data: Dict, meeting: Meeting, db: Session) -> int:
    """Saves tasks from Gemini's response to the database, linked to a meeting."""
    meeting.summary_minutes = extracted_data.get("minutes", "No summary generated.")
    task_items = extracted_data.get("tasks", []) or []
    
    created_count = 0
    for item in task_items:
        description = str(item.get("description", "")).strip()
        if not description:
            continue
        
        assignee_name = str(item.get("assignee", "")).strip()
        if not assignee_name:
            continue # Skip tasks with no assignee
        
        assignee = get_or_create_user(db, assignee_name)
        task = Task(
            description=description,
            due_date=item.get("due_date"),
            status="To Do",
            assignee_id=assignee.id,
            meeting_id=meeting.id, # Link task to the meeting
        )
        db.add(task)
        created_count += 1
    
    db.commit()
    return created_count


# --- USER Endpoints ---

@app.get("/users/me", response_model=UserOut, summary="Get Current User")
async def read_users_me(current_user: User = Depends(auth_dependency)):
    return current_user

@app.get("/users/me/tasks", response_model=List[TaskOut], summary="List My Tasks")
async def list_my_tasks(current_user: User = Depends(auth_dependency), db: Session = Depends(get_db)):
    """Returns a list of all tasks assigned to the current user."""
    tasks = db.query(Task).options(joinedload(Task.assignee)).filter(Task.assignee_id == current_user.id).order_by(Task.id.desc()).all()
    return tasks


# --- ADMIN Endpoints ---

@app.post("/admin/process-meeting/", response_model=ProcessResult, summary="[Admin] Process a New Meeting")
async def process_meeting(
    title: str = Form(...),
    date: str = Form(...),
    transcript: Optional[str] = Form(None),
    audio_file: Optional[UploadFile] = File(None),
    admin_user: User = Depends(admin_dependency),
    db: Session = Depends(get_db)
):
    """Admin-only endpoint to process a meeting from audio OR a transcript."""
    if not transcript and not audio_file:
        raise HTTPException(status_code=400, detail="Either a transcript or an audio file must be provided.")
    if transcript and audio_file:
        raise HTTPException(status_code=400, detail="Provide either a transcript or an audio file, not both.")

    # Create the meeting record first
    new_meeting = Meeting(title=title, date=date, processed_by_id=admin_user.id)
    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)

    source_content = transcript
    if audio_file:
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        with tempfile.NamedTemporaryFile(delete=False, suffix=audio_file.filename) as temp:
            shutil.copyfileobj(audio_file.file, temp)
            temp_path = temp.name
        
        try:
            uploaded_file = genai.upload_file(path=temp_path, display_name=audio_file.filename)
            response = model.generate_content([_get_gemini_prompt(), uploaded_file])
            source_content = response.text
        finally:
            os.unlink(temp_path)
    
    # Process the text content (either from transcript or audio)
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    response = model.generate_content([_get_gemini_prompt(), source_content])
    extracted_data = _parse_gemini_response(response.text)
    
    created_tasks = _process_and_save(extracted_data, new_meeting, db)

    return ProcessResult(meeting_id=new_meeting.id, created_tasks=created_tasks)


@app.get("/admin/stats", response_model=AdminDashboardStats, summary="[Admin] Get Dashboard Stats")
async def get_admin_stats(admin_user: User = Depends(admin_dependency), db: Session = Depends(get_db)):
    total_meetings = db.query(func.count(Meeting.id)).scalar()
    total_tasks = db.query(func.count(Task.id)).scalar()
    tasks_todo = db.query(func.count(Task.id)).filter(Task.status == "To Do").scalar()
    tasks_completed = db.query(func.count(Task.id)).filter(Task.status.in_(["Completed", "Verified"])).scalar()
    
    return AdminDashboardStats(
        total_meetings=total_meetings or 0,
        total_tasks=total_tasks or 0,
        tasks_todo=tasks_todo or 0,
        tasks_completed=tasks_completed or 0,
    )

@app.get("/admin/tasks", response_model=List[TaskOut], summary="[Admin] List All Tasks")
async def list_all_tasks(admin_user: User = Depends(admin_dependency), db: Session = Depends(get_db)):
    """Returns a list of all tasks from all users."""
    tasks = db.query(Task).options(joinedload(Task.assignee)).order_by(Task.id.desc()).all()
    return tasks

@app.patch("/admin/tasks/{task_id}", response_model=TaskOut, summary="[Admin] Update a Task")
async def update_task_status(
    task_id: int, task_update: TaskUpdate, admin_user: User = Depends(admin_dependency), db: Session = Depends(get_db)
):
    """Updates the status of a specific task."""
    db_task = db.query(Task).options(joinedload(Task.assignee)).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db_task.status = task_update.status
    db.commit()
    db.refresh(db_task)
    return db_task