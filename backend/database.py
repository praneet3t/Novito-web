# backend/database.py
from typing import Optional, List, Generator
from datetime import datetime, timedelta

from sqlalchemy import (
    create_engine,
    Integer,
    String,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
    Float,
    Enum as SQLEnum,
)
import enum
from sqlalchemy.orm import (
    declarative_base,
    relationship,
    sessionmaker,
    Session,
    Mapped,
    mapped_column,
)

# --- Database Configuration ---
DATABASE_URL = "sqlite:///./meeting_agent.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- ORM Models ---


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(256), nullable=False)  # plain text (demo only)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    tokens: Mapped[List["Token"]] = relationship("Token", back_populates="user", cascade="all, delete-orphan")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="assignee", foreign_keys="Task.assignee_id", cascade="all, delete-orphan")
    meetings_processed: Mapped[List["Meeting"]] = relationship("Meeting", back_populates="processed_by", cascade="all, delete-orphan")


class Token(Base):
    __tablename__ = "tokens"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    token: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="tokens")


class Meeting(Base):
    __tablename__ = "meetings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(256), index=True, nullable=False)
    date: Mapped[str] = mapped_column(String(64), nullable=False)
    summary_minutes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    processed_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    processed_by: Mapped[Optional["User"]] = relationship("User", back_populates="meetings_processed")

    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="meeting", cascade="all, delete-orphan")


class EffortTag(enum.Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    due_date: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="To Do")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Agile fields
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    effort_tag: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    timestamp_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Tracking fields
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    blocker_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Submission & Verification
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    submission_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    submission_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    verified_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    verification_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Scrum fields
    story_points: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sprint_position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    acceptance_criteria: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    definition_of_done: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    assignee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id"), nullable=False)
    bundle_id: Mapped[Optional[int]] = mapped_column(ForeignKey("bundle_groups.id"), nullable=True)
    workcycle_id: Mapped[Optional[int]] = mapped_column(ForeignKey("work_cycles.id"), nullable=True)

    assignee: Mapped["User"] = relationship("User", back_populates="tasks", foreign_keys=[assignee_id])
    verified_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[verified_by_id])
    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="tasks")
    bundle: Mapped[Optional["BundleGroup"]] = relationship("BundleGroup", back_populates="tasks")
    workcycle: Mapped[Optional["WorkCycle"]] = relationship("WorkCycle", back_populates="tasks")


class WorkCycle(Base):
    __tablename__ = "work_cycles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    start_date: Mapped[str] = mapped_column(String(64), nullable=False)
    end_date: Mapped[str] = mapped_column(String(64), nullable=False)
    goal: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    owner: Mapped["User"] = relationship("User")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="workcycle")
    snapshots: Mapped[List["ProgressSnapshot"]] = relationship("ProgressSnapshot", back_populates="workcycle", cascade="all, delete-orphan")


class BundleGroup(Base):
    __tablename__ = "bundle_groups"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    owner: Mapped["User"] = relationship("User")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="bundle")


class ProgressSnapshot(Base):
    __tablename__ = "progress_snapshots"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    workcycle_id: Mapped[int] = mapped_column(ForeignKey("work_cycles.id"), nullable=False)
    snapshot_date: Mapped[str] = mapped_column(String(64), nullable=False)
    remaining_effort: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    workcycle: Mapped["WorkCycle"] = relationship("WorkCycle", back_populates="snapshots")


# --- Utility functions ---


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_or_create_user(db: Session, username: str, password: str = "changeme", is_admin: bool = False) -> User:
    user = db.query(User).filter(User.username == username).first()
    if user:
        return user
    new_user = User(username=username, password=password, is_admin=is_admin)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def create_token_for_user(db: Session, user: User, days_valid: int = 7) -> str:
    import uuid
    token_str = uuid.uuid4().hex
    expires = datetime.utcnow() + timedelta(days=days_valid)
    tok = Token(token=token_str, user_id=user.id, expires_at=expires)
    db.add(tok)
    db.commit()
    db.refresh(tok)
    return token_str


def seed_demo_users(db: Session) -> None:
    demo_users = {
        "Priya": {"password": "priya123", "is_admin": False},
        "Arjun": {"password": "arjun456", "is_admin": False},
        "Raghav": {"password": "raghav789", "is_admin": False},
        "Admin": {"password": "admin123", "is_admin": True},
    }
    for username, details in demo_users.items():
        if not db.query(User).filter(User.username == username).first():
            user = User(username=username, password=details["password"], is_admin=details["is_admin"])
            db.add(user)
    db.commit()


# Initialize DB on import and seed if empty
init_db()
with SessionLocal() as db:
    if db.query(User).count() == 0:
        seed_demo_users(db)
