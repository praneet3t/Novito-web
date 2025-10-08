from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import Task, Meeting, User

def get_daily_briefing(db: Session):
    today = datetime.utcnow().date()
    
    # Tasks completed today
    completed_today = db.query(Task).filter(
        Task.status == "Done",
        func.date(Task.last_updated) == today
    ).count()
    
    # Blocked tasks
    blocked = db.query(Task).filter(Task.is_blocked == True, Task.status != "Done").all()
    
    # Risk tasks
    risks = db.query(Task).filter(Task.is_potential_risk == True, Task.status != "Done").all()
    
    # High priority pending
    high_priority = db.query(Task).filter(
        Task.priority >= 8,
        Task.status != "Done",
        Task.is_approved == True
    ).order_by(Task.priority.desc()).limit(5).all()
    
    # Overdue tasks
    overdue = db.query(Task).filter(
        Task.due_date < today.isoformat(),
        Task.status != "Done"
    ).all()
    
    # Manager approval pending
    pending_approval = db.query(Task).filter(Task.status == "Manager Approval Pending").count()
    
    # SLA breached
    sla_breached = db.query(Task).filter(
        Task.status == "Submitted",
        Task.verification_deadline_at < datetime.utcnow(),
        Task.verified_at == None
    ).count()
    
    return {
        "date": today.isoformat(),
        "completed_today": completed_today,
        "blocked_count": len(blocked),
        "blocked_tasks": [{"id": t.id, "description": t.description, "reason": t.blocker_reason} for t in blocked[:3]],
        "risk_count": len(risks),
        "risk_tasks": [{"id": t.id, "description": t.description, "reason": t.risk_reason} for t in risks[:3]],
        "high_priority": [{"id": t.id, "description": t.description, "priority": t.priority, "due_date": t.due_date} for t in high_priority],
        "overdue_count": len(overdue),
        "overdue_tasks": [{"id": t.id, "description": t.description, "due_date": t.due_date} for t in overdue[:3]],
        "pending_approval": pending_approval,
        "sla_breached": sla_breached
    }

def get_productivity_analytics(db: Session, days=7):
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Meeting time
    meetings = db.query(Meeting).filter(Meeting.created_at >= start_date).count()
    
    # Task completion rate
    total_tasks = db.query(Task).filter(Task.created_at >= start_date).count()
    completed_tasks = db.query(Task).filter(
        Task.created_at >= start_date,
        Task.status == "Done"
    ).count()
    
    # Average time to complete
    completed = db.query(Task).filter(
        Task.status == "Done",
        Task.created_at >= start_date
    ).all()
    
    avg_completion_time = 0
    if completed:
        times = [(t.last_updated - t.created_at).total_seconds() / 3600 for t in completed]
        avg_completion_time = sum(times) / len(times)
    
    # Blocker frequency
    blocked_count = db.query(Task).filter(
        Task.is_blocked == True,
        Task.created_at >= start_date
    ).count()
    
    return {
        "period_days": days,
        "meetings_held": meetings,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "completion_rate": round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1),
        "avg_completion_hours": round(avg_completion_time, 1),
        "blocked_tasks": blocked_count,
        "blocker_rate": round((blocked_count / total_tasks * 100) if total_tasks > 0 else 0, 1)
    }

def detect_blockers_from_transcript(transcript: str):
    blocker_keywords = ["blocked", "stuck", "waiting", "can't proceed", "dependency", "issue", "problem", "blocker"]
    lines = transcript.lower().split('\n')
    blockers = []
    
    for line in lines:
        if any(keyword in line for keyword in blocker_keywords):
            blockers.append(line.strip())
    
    return blockers
