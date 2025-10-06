from datetime import datetime, timedelta
from database import SessionLocal, get_or_create_user, Meeting, Task, WorkCycle, BundleGroup

def seed_example_data():
    db = SessionLocal()
    
    # Create users
    admin = get_or_create_user(db, "Admin", "admin123", True)
    priya = get_or_create_user(db, "Priya", "priya123", False)
    arjun = get_or_create_user(db, "Arjun", "arjun456", False)
    raghav = get_or_create_user(db, "Raghav", "raghav789", False)
    
    # Create example meetings
    meeting1 = Meeting(
        title="Q1 Planning Meeting",
        date=(datetime.now() - timedelta(days=2)).isoformat(),
        summary_minutes="Discussed Q1 goals, resource allocation, and sprint planning. Team agreed on priorities for authentication module and API optimization.",
        processed_by_id=admin.id
    )
    db.add(meeting1)
    db.commit()
    db.refresh(meeting1)
    
    meeting2 = Meeting(
        title="Sprint Retrospective",
        date=(datetime.now() - timedelta(days=5)).isoformat(),
        summary_minutes="Reviewed last sprint performance. Identified bottlenecks in deployment process. Team committed to improving code review turnaround time.",
        processed_by_id=admin.id
    )
    db.add(meeting2)
    db.commit()
    db.refresh(meeting2)
    
    # Create work cycle
    cycle = WorkCycle(
        name="Q1 Sprint 1",
        start_date=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
        end_date=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        goal="Complete authentication module and optimize API endpoints",
        owner_id=admin.id
    )
    db.add(cycle)
    db.commit()
    db.refresh(cycle)
    
    # Create bundle
    bundle = BundleGroup(
        title="Authentication Feature",
        description="All tasks related to user authentication implementation",
        owner_id=admin.id
    )
    db.add(bundle)
    db.commit()
    db.refresh(bundle)
    
    # Create example tasks
    tasks_data = [
        {"desc": "Implement OAuth2 login flow", "assignee": priya, "meeting": meeting1, "priority": 9, "effort": "large", "approved": True, "status": "Doing", "due": 3},
        {"desc": "Design user profile API endpoints", "assignee": arjun, "meeting": meeting1, "priority": 8, "effort": "medium", "approved": True, "status": "To Do", "due": 5},
        {"desc": "Write unit tests for authentication", "assignee": raghav, "meeting": meeting1, "priority": 7, "effort": "medium", "approved": True, "status": "To Do", "due": 7},
        {"desc": "Update API documentation", "assignee": priya, "meeting": meeting2, "priority": 6, "effort": "small", "approved": False, "status": "To Do", "due": 10},
        {"desc": "Optimize database queries for user lookup", "assignee": arjun, "meeting": meeting2, "priority": 8, "effort": "medium", "approved": False, "status": "To Do", "due": 6},
        {"desc": "Setup CI/CD pipeline for automated testing", "assignee": raghav, "meeting": meeting2, "priority": 9, "effort": "large", "approved": True, "status": "To Do", "due": 4},
        {"desc": "Review and merge authentication PR", "assignee": admin, "meeting": meeting1, "priority": 10, "effort": "small", "approved": True, "status": "To Do", "due": 2},
    ]
    
    for i, td in enumerate(tasks_data):
        task = Task(
            description=td["desc"],
            assignee_id=td["assignee"].id,
            meeting_id=td["meeting"].id,
            priority=td["priority"],
            effort_tag=td["effort"],
            is_approved=td["approved"],
            status=td["status"],
            due_date=(datetime.now() + timedelta(days=td["due"])).strftime("%Y-%m-%d"),
            confidence=0.85 + (i * 0.02),
            bundle_id=bundle.id if i < 3 else None,
            workcycle_id=cycle.id if td["approved"] else None
        )
        db.add(task)
    
    db.commit()
    db.close()
    print("Example data seeded successfully!")

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    seed_example_data()
