from typing import Optional, List
from sqlalchemy import create_engine, ForeignKey, String, Boolean, Text
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session, Mapped, mapped_column

# --- Database Configuration ---
DATABASE_URL = "sqlite:///./meeting_agent.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- ORM Models ---

class User(Base):
    """Represents a user (participant or admin) in the system."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    tasks: Mapped[List["Task"]] = relationship(back_populates="assignee")


class Meeting(Base):
    """Represents a single meeting record processed by an admin."""
    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True, nullable=False)
    date: Mapped[str] = mapped_column(String, nullable=False)
    summary_minutes: Mapped[str] = mapped_column(Text, nullable=True)

    # Foreign key to link to the admin who processed the meeting
    processed_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    # Relationships
    tasks: Mapped[List["Task"]] = relationship(back_populates="meeting")


class Task(Base):
    """Represents an action item, now linked to a specific meeting."""
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    description: Mapped[str] = mapped_column(String, nullable=False)
    due_date: Mapped[Optional[str]] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, nullable=False, default="To Do")

    # Foreign key to the user this task is assigned to
    assignee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    # Foreign key to the meeting this task originated from
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id"), nullable=False)
    
    # Relationships
    assignee: Mapped["User"] = relationship(back_populates="tasks")
    meeting: Mapped["Meeting"] = relationship(back_populates="tasks")


# --- Database Utility Functions ---

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_or_create_user(db: Session, username: str) -> User:
    user = db.query(User).filter(User.username.ilike(username)).first()
    if user:
        return user
    
    new_user = User(username=username, password="default_password", is_admin=False)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def seed_demo_users(db: Session):
    demo_users = {
        "Priya": {"password": "priya123", "is_admin": False},
        "Arjun": {"password": "arjun456", "is_admin": False},
        "Raghav": {"password": "raghav789", "is_admin": False},
        "Admin": {"password": "admin123", "is_admin": True},
    }
    for username, details in demo_users.items():
        if not db.query(User).filter(User.username.ilike(username)).first():
            user = User(
                username=username,
                password=details["password"],
                is_admin=details["is_admin"]
            )
            db.add(user)
    db.commit()

# --- Initialize Database ---
init_db()
with SessionLocal() as db:
    seed_demo_users(db)