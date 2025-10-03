import json
import os
import shutil
import tempfile
from typing import Dict, List, Optional

import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import (FastAPI, Depends, File, HTTPException, Request,
                     UploadFile, status)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session, joinedload

try:
    from backend.database import User, Task, get_db, get_or_create_user
except ImportError:
    from database import User, Task, get_db, get_or_create_user

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

app = FastAPI(title="Meeting Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://12-7.0.0.1:5173"],
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

class TaskUpdate(BaseModel):
    status: str

class ProcessResult(BaseModel):
    minutes: str
    created_tasks: int


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
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource."
        )
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
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


def _process_and_save_tasks(extracted_data: Dict, current_user: User, db: Session) -> ProcessResult:
    minutes = extracted_data.get("minutes", "No summary generated.")
    task_items = extracted_data.get("tasks", []) or []
    created_count = 0
    for item in task_items:
        description = str(item.get("description", "")).strip()
        if not description:
            continue
        
        assignee_name = str(item.get("assignee", "")).strip() or current_user.username
        assignee = get_or_create_user(db, assignee_name)

        task = Task(
            description=description,
            due_date=item.get("due_date"),
            status="To Do",
            assignee_id=assignee.id
        )
        db.add(task)
        created_count += 1
    
    db.commit()
    return ProcessResult(minutes=minutes, created_tasks=created_count)


# --- API Endpoints ---

@app.get("/", summary="Health Check")
async def root():
    return {"status": "ok", "service": "Meeting Agent API"}


@app.get("/users/me", response_model=UserOut, summary="Get Current User")
async def read_users_me(current_user: User = Depends(auth_dependency)):
    return current_user


@app.get("/users/me/tasks", response_model=List[TaskOut], summary="List My Tasks")
async def list_my_tasks(current_user: User = Depends(auth_dependency), db: Session = Depends(get_db)):
    tasks = db.query(Task).options(joinedload(Task.assignee)).filter(Task.assignee_id == current_user.id).order_by(Task.id.desc()).all()
    return tasks


@app.post("/process-audio/", response_model=ProcessResult, summary="Process Meeting Audio File")
async def process_audio_file(
    file: UploadFile = File(...),
    current_user: User = Depends(auth_dependency),
    db: Session = Depends(get_db)
):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=501, detail="Not implemented: GEMINI_API_KEY not configured.")

    model = genai.GenerativeModel("gemini-2.5-flash")

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as temp_file:
            temp_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)

        uploaded_file = genai.upload_file(
            path=temp_path,
            display_name=file.filename
        )

        prompt = _get_gemini_prompt()
        response = model.generate_content([prompt, uploaded_file])
        
        extracted_data = _parse_gemini_response(response.text)
        
        return _process_and_save_tasks(extracted_data, current_user, db)

    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)


# --- Admin Endpoints ---

@app.get("/admin/tasks", response_model=List[TaskOut], summary="[Admin] List All Tasks")
async def list_all_tasks(
    admin_user: User = Depends(admin_dependency), db: Session = Depends(get_db)
):
    tasks = db.query(Task).options(joinedload(Task.assignee)).order_by(Task.id.desc()).all()
    return tasks


@app.patch("/admin/tasks/{task_id}", response_model=TaskOut, summary="[Admin] Update a Task")
async def update_task_status(
    task_id: int,
    task_update: TaskUpdate,
    admin_user: User = Depends(admin_dependency),
    db: Session = Depends(get_db),
):
    db_task = db.query(Task).options(joinedload(Task.assignee)).filter(Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db_task.status = task_update.status
    db.commit()
    db.refresh(db_task)
    return db_task