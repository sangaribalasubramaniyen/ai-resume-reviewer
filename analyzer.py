"""
analyzer.py
-----------
Business logic for AI-powered resume analysis.

This file talks to the Claude API. It is kept separate from main.py
(which handles the web routes) so each file has one clear job.
"""

import os
import json
from anthropic import Anthropic

# Read the API key from the environment (loaded from .env in main.py).
# We never hard-code the key in the source — that would leak it to GitHub.
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# The model we ask to do the analysis.
MODEL = "claude-sonnet-4-6"


# This is the "instructions" we give Claude. Good prompt design is what
# turns a generic chatbot into a focused resume reviewer.
SYSTEM_PROMPT = """You are an expert technical recruiter and ATS (Applicant Tracking System) specialist.
You review software-engineering resumes and give honest, actionable feedback.

You MUST respond with ONLY valid JSON (no markdown, no extra text) in exactly this shape:
{
  "ats_score": <integer 0-100>,
  "summary": "<one or two sentence overall impression>",
  "strengths": ["<strength 1>", "<strength 2>", "..."],
  "weaknesses": ["<weakness 1>", "<weakness 2>", "..."],
  "missing_keywords": ["<important keyword the resume lacks>", "..."],
  "suggestions": ["<specific, actionable improvement>", "..."]
}

Scoring guide for ats_score:
- 90-100: excellent, ATS-friendly, strong impact statements
- 70-89: good, minor gaps
- 50-69: average, needs clearer structure or metrics
- below 50: weak, hard for ATS to parse or missing key sections
"""


def analyze_resume(resume_text: str) -> dict:
    """
    Send extracted resume text to Claude and return structured feedback.

    Returns a Python dict (parsed from Claude's JSON response).
    """
    # We send the resume text as the user's message. max_tokens caps the
    # length of Claude's reply so we don't get runaway cost.
    message = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Review this resume and return the JSON feedback:\n\n{resume_text}",
            }
        ],
    )

    # Claude's reply text is in message.content[0].text
    raw_reply = message.content[0].text.strip()

    # Defensive: if the model ever wraps JSON in ```json fences, strip them.
    if raw_reply.startswith("```"):
        raw_reply = raw_reply.strip("`")
        raw_reply = raw_reply.replace("json", "", 1).strip()

    # Turn the JSON string into a real Python dict so FastAPI can return it.
    return json.loads(raw_reply)
