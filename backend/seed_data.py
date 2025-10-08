from datetime import datetime, timedelta
from database import SessionLocal, get_or_create_user, Meeting, Task, WorkCycle, BundleGroup, Team, TeamMember, Notification

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
    
    # Create teams
    frontend_team = Team(name="Frontend Team", description="UI/UX development team")
    backend_team = Team(name="Backend Team", description="API and database team")
    db.add(frontend_team)
    db.add(backend_team)
    db.commit()
    db.refresh(frontend_team)
    db.refresh(backend_team)
    
    # Add team members
    db.add(TeamMember(team_id=frontend_team.id, user_id=priya.id, role="member"))
    db.add(TeamMember(team_id=backend_team.id, user_id=arjun.id, role="lead"))
    db.add(TeamMember(team_id=backend_team.id, user_id=raghav.id, role="member"))
    db.commit()
    
    # Create bundle
    bundle = BundleGroup(
        title="Authentication Feature",
        description="All tasks related to user authentication implementation",
        owner_id=admin.id
    )
    db.add(bundle)
    db.commit()
    db.refresh(bundle)
    
    # Create example tasks with all new features
    tasks_data = [
        # Regular tasks
        {"desc": "Implement OAuth2 login flow", "assignee": priya, "meeting": meeting1, "priority": 9, "effort": "large", "approved": True, "status": "Doing", "due": 3, "progress": 60, "sp": 8, "team": frontend_team.id},
        {"desc": "Design user profile API endpoints", "assignee": arjun, "meeting": meeting1, "priority": 8, "effort": "medium", "approved": True, "status": "To Do", "due": 5, "progress": 0, "sp": 5, "team": backend_team.id},
        
        # Task with risk flag
        {"desc": "Integrate payment gateway API", "assignee": raghav, "meeting": meeting1, "priority": 7, "effort": "large", "approved": True, "status": "To Do", "due": 7, "progress": 0, "sp": 13, "risk": True, "risk_reason": "Waiting for payment provider API credentials", "team": backend_team.id},
        
        # Task needing manager approval (large story points)
        {"desc": "Refactor entire authentication system", "assignee": arjun, "meeting": meeting2, "priority": 8, "effort": "large", "approved": False, "status": "Manager Approval Pending", "due": 14, "progress": 0, "sp": 21, "team": backend_team.id},
        
        # Task with low confidence (needs priority review)
        {"desc": "Update API documentation", "assignee": priya, "meeting": meeting2, "priority": 4, "effort": "small", "approved": False, "status": "To Do", "due": 10, "progress": 0, "sp": 2, "confidence": 0.6, "needs_review": True, "team": frontend_team.id},
        
        # Task ready for submission
        {"desc": "Create login page UI", "assignee": priya, "meeting": meeting1, "priority": 8, "effort": "medium", "approved": True, "status": "Doing", "due": 2, "progress": 100, "sp": 5, "team": frontend_team.id},
        
        # Submitted task (pending verification)
        {"desc": "Setup database migrations", "assignee": raghav, "meeting": meeting2, "priority": 7, "effort": "medium", "approved": True, "status": "Submitted", "due": 1, "progress": 100, "sp": 3, "submitted": True, "team": backend_team.id},
        
        # Captured task (from quick capture)
        {"desc": "Research new UI framework options", "assignee": priya, "meeting": meeting1, "priority": 5, "effort": "small", "approved": False, "status": "Capture Inbox", "due": 15, "progress": 0, "sp": 2, "team": frontend_team.id},
        
        # Task planned for tomorrow
        {"desc": "Fix responsive layout issues", "assignee": priya, "meeting": meeting2, "priority": 6, "effort": "small", "approved": True, "status": "Planned for Tomorrow", "due": 1, "progress": 30, "sp": 2, "team": frontend_team.id},
    ]
    
    for i, td in enumerate(tasks_data):
        due_date = (datetime.now() + timedelta(days=td["due"])).strftime("%Y-%m-%d")
        confidence = td.get("confidence", 0.85 + (i * 0.02))
        
        # Calculate suggested focus time
        effort_hours = {"small": 1, "medium": 3, "large": 6}
        hours = effort_hours.get(td["effort"], 3)
        suggested_time = datetime.now() + timedelta(days=td["due"]) - timedelta(hours=hours)
        
        task = Task(
            description=td["desc"],
            assignee_id=td["assignee"].id,
            meeting_id=td["meeting"].id,
            priority=td["priority"],
            effort_tag=td["effort"],
            is_approved=td["approved"],
            status=td["status"],
            due_date=due_date,
            confidence=confidence,
            progress=td.get("progress", 0),
            story_points=td.get("sp"),
            bundle_id=bundle.id if i < 3 else None,
            workcycle_id=cycle.id if td["approved"] and td["status"] != "Manager Approval Pending" else None,
            team_id=td.get("team"),
            is_potential_risk=td.get("risk", False),
            risk_reason=td.get("risk_reason"),
            needs_priority_review=td.get("needs_review", False),
            suggested_focus_time=suggested_time,
            submitted_at=datetime.now() - timedelta(hours=12) if td.get("submitted") else None,
            submission_notes="Completed all requirements. Tested locally and on staging." if td.get("submitted") else None,
            submission_url="https://github.com/example/pr/123" if td.get("submitted") else None,
            verification_deadline_at=datetime.now() + timedelta(hours=12) if td.get("submitted") else None
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        
        # Create notifications for some tasks
        if td.get("submitted"):
            notif = Notification(
                user_id=td["assignee"].id,
                message=f"Task submitted for review: {td['desc']}",
                task_id=task.id
            )
            db.add(notif)
        
        if td.get("risk"):
            notif = Notification(
                user_id=admin.id,
                message=f"Risk detected: {td['desc']} - {td.get('risk_reason')}",
                task_id=task.id
            )
            db.add(notif)
        
        if td["status"] == "Manager Approval Pending":
            notif = Notification(
                user_id=admin.id,
                message=f"Manager approval required: {td['desc']} ({td.get('sp')} story points)",
                task_id=task.id
            )
            db.add(notif)
    
    # Add some general notifications
    db.add(Notification(user_id=priya.id, message="Welcome to Meeting Agent! Check out the Quick Capture feature."))
    db.add(Notification(user_id=arjun.id, message="You have 2 tasks due this week. Check Priority Queue."))
    db.add(Notification(user_id=raghav.id, message="Your submitted task is pending verification."))
    
    db.commit()
    db.close()
    print("Example data seeded successfully with all enterprise features!")
    print("\nFeature Examples Created:")
    print("- AI Proactive Scheduling: All tasks have suggested_focus_time")
    print("- Risk Detection: 'Integrate payment gateway' flagged as risk")
    print("- Quick Capture: 'Research UI framework' in Capture Inbox")
    print("- Manager Approval: 'Refactor authentication' needs approval (21 SP)")
    print("- Low Confidence: 'Update documentation' needs priority review (0.6 confidence)")
    print("- SLA Tracking: 'Setup database migrations' submitted 12h ago")
    print("- Teams: Frontend and Backend teams created with members")
    print("- Notifications: Multiple notifications for users and admin")
    print("- Daily Shutdown: 'Fix responsive layout' marked for tomorrow")
    print("\nLogin as Admin (Admin/admin123) or Priya (Priya/priya123) to see features!")

if __name__ == "__main__":
    try:
        import sys
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass
    seed_example_data()
