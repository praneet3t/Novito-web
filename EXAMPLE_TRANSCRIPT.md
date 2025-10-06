# Example Meeting Transcripts

Use these example transcripts to test the AI task extraction feature.

## Example 1: Sprint Planning Meeting

```
Meeting Date: 2024-01-15
Attendees: Priya, Arjun, Raghav, Admin

Admin: Good morning everyone. Let's plan our next sprint. We need to focus on the authentication module.

Priya: I can take the OAuth2 implementation. It's a big task but I think I can have it done by January 22nd. I'll need about a week for this.

Arjun: I'll work on designing the API endpoints for user profiles. Should take me around 3-4 days. I can start right after this meeting and finish by January 19th.

Raghav: Once Priya finishes the OAuth implementation, I'll write comprehensive unit tests. I estimate this will take about 5 days, so targeting January 27th.

Admin: Great. I also need someone to update our API documentation. Priya, can you handle that after OAuth?

Priya: Sure, that's a small task. I can do it by January 30th.

Arjun: We should also optimize the database queries for user lookup. It's currently slow. I can tackle this alongside the API work. Medium effort, should be done by January 21st.

Raghav: Don't forget we need to setup the CI/CD pipeline for automated testing. That's critical and fairly complex. I'll prioritize this - aiming for January 19th.

Admin: Excellent. I'll handle the code review for the authentication PR. That's blocking our deployment, so it's top priority. I'll get it done by January 17th.

Priya: One more thing - we should implement password reset functionality. I can add that to my list for January 25th. It's medium complexity.

Admin: Perfect. Let's make this sprint count!
```

## Example 2: Bug Triage Meeting

```
Meeting Date: 2024-01-16
Attendees: Priya, Arjun, Raghav

Priya: We have several critical bugs to address. First, users are reporting login failures on mobile devices.

Arjun: I can investigate the mobile login issue. Sounds urgent. I'll prioritize this and have a fix by January 18th. Probably a medium effort task.

Raghav: There's also a memory leak in the session management. I noticed it yesterday. This is critical and complex. I'll need to dive deep into this - targeting January 20th for a fix.

Priya: The email verification system is broken. Emails aren't being sent. I can fix this quickly, it's a small task. I'll have it done by tomorrow, January 17th.

Arjun: We're also seeing slow response times on the dashboard. I'll profile the code and optimize it. This is high priority, medium effort. Should be done by January 19th.

Raghav: Don't forget the security vulnerability in the password reset flow that was reported. That's critical. I'll patch it immediately - today if possible, January 16th.

Priya: I'll also add better error logging to help us catch these issues earlier. Small task, can do it by January 18th.

Arjun: We need to update our dependencies too. Some have security patches. I'll handle that by January 21st. It's a medium effort task.

Raghav: Lastly, the API rate limiting isn't working correctly. I'll fix that by January 22nd. Medium complexity.
```

## Example 3: Feature Discussion

```
Meeting Date: 2024-01-17
Attendees: Priya, Arjun, Raghav, Admin

Admin: Today we're discussing new features for Q1. Let's start with the most requested ones.

Priya: Users want dark mode. I can implement that. It's a large task with lots of UI changes. I'll need two weeks, so February 1st deadline.

Arjun: We should add two-factor authentication. That's critical for security. Large effort, I estimate 10 days. I can have it ready by January 30th.

Raghav: Social login integration - Google and GitHub. I'll handle this. It's medium complexity. Targeting January 28th.

Admin: We need analytics dashboard for admins. Arjun, can you take this?

Arjun: Yes, but it's a large task. I'll need until February 5th for a complete implementation.

Priya: File upload functionality for user profiles. Medium task, I can do it by January 26th.

Raghav: We should implement real-time notifications using WebSockets. That's complex and large. I'll need until February 3rd.

Admin: Export functionality - users want to export their data as CSV. Priya?

Priya: Sure, that's a small task. I can have it done by January 24th.

Arjun: We need better search functionality with filters. Medium effort, I'll target January 29th.

Raghav: API versioning should be implemented before we add more features. Small but important. I'll do it by January 23rd.

Admin: Great planning session. Let's execute!
```

## How to Use

1. Login as Admin (Admin/admin123)
2. Go to "Process Meeting" section
3. Copy one of the transcripts above
4. Paste into the "Transcript" field
5. Add a title (e.g., "Sprint Planning Meeting")
6. Click "Process"
7. Go to "Review Queue" to see AI-extracted tasks
8. Approve tasks to add them to the priority queue

## Expected AI Output

The AI should extract:
- **Assignee**: Person's name from the transcript
- **Description**: Clear task description
- **Due Date**: Mentioned deadline in ISO format
- **Priority**: 1-10 based on urgency keywords (critical, urgent, blocking)
- **Effort**: small/medium/large based on complexity mentions
- **Confidence**: 0.8-1.0 for clear tasks, lower for ambiguous ones
