from typing import Optional
from sqlalchemy import create_engine, ForeignKey, String, Boolean
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session, Mapped, mapped_column

# --- Database Configuration ---
DATABASE_URL = "sqlite:///./meeting_agent.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# --- ORM Models ---

class User(Base):
    """Represents a user in the system."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    tasks: Mapped[list["Task"]] = relationship(back_populates="assignee")


class Task(Base):
    """Represents an action item extracted from a meeting."""
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    description: Mapped[str] = mapped_column(String, nullable=False)
    due_date: Mapped[Optional[str]] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, nullable=False, default="To Do")

    assignee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    assignee: Mapped["User"] = relationship(back_populates="tasks")


# --- Database Utility Functions ---

def init_db() -> None:
    """Creates all database tables based on the models."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency injector that provides a database session for a single request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_or_create_user(db: Session, username: str) -> User:
    """Finds a user by username (case-insensitive) or creates them with a default password."""
    user = db.query(User).filter(User.username.ilike(username)).first()
    if user:
        return user
    
    new_user = User(username=username, password="default_password", is_admin=False)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def seed_demo_users(db: Session) -> None:
    """Creates initial demo users if they are not already in the database."""
    demo_users = {
        "Priya": {"password": "priya123", "is_admin": False},
        "Arjun": {"password": "arjun456", "is_admin": False},
        "Raghav": {"password": "raghav789", "is_admin": False},
        "Admin": {"password": "admin123", "is_admin": True},
    }
    for username, details in demo_users.items():
        user_exists = db.query(User).filter(User.username.ilike(username)).first()
        if not user_exists:
            user = User(
                username=username,
                password=details["password"],
                is_admin=details["is_admin"]
            )
            db.add(user)
    db.commit()


# --- Initialize Database on First Import ---
init_db()

with SessionLocal() as db_session:
    seed_demo_users(db_session)