import os
import json
import google.generativeai as genai
from typing import List, Dict

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash-exp")

def extract_tasks_from_transcript(transcript: str) -> List[Dict]:
    prompt = f"""Analyze this meeting transcript and extract action items/tasks.
For each task, identify:
- assignee: person's name who should do it
- description: clear task description
- due_date: deadline if mentioned (ISO format YYYY-MM-DD)
- priority: 1-10 based on urgency
- effort_tag: "small", "medium", or "large"
- confidence: 0.0-1.0 how confident you are this is a real task

Return ONLY valid JSON array, no markdown:
[{{"assignee": "Name", "description": "Task", "due_date": "2024-01-15", "priority": 5, "effort_tag": "medium", "confidence": 0.9}}]

Transcript:
{transcript}"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except Exception as e:
        print(f"Gemini error: {e}")
        return []

def generate_meeting_summary(transcript: str) -> str:
    prompt = f"""Summarize this meeting in 2-3 sentences focusing on key decisions and outcomes.

Transcript:
{transcript}"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return transcript[:500] + "..."
