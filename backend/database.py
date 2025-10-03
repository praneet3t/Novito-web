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
)
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
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="assignee", cascade="all, delete-orphan")
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


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    due_date: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="To Do")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    assignee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id"), nullable=False)

    assignee: Mapped["User"] = relationship("User", back_populates="tasks")
    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="tasks")


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
