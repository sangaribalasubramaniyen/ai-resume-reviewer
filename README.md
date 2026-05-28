# AI Resume Reviewer

An AI-powered resume analysis API built with FastAPI and Claude.

## Features (Planned)

- Upload resume (PDF/DOCX)
- AI-powered analysis using Claude API
- ATS compatibility score
- Section-wise feedback (Summary, Experience, Skills, Education)
- Job description matching
- Keyword gap analysis
- Improvement suggestions

## Tech Stack

- **Backend:** FastAPI (Python 3.14)
- **AI:** Anthropic Claude API
- **Database:** PostgreSQL
- **PDF Parsing:** PyPDF2, pdfplumber
- **Auth:** JWT
- **Deployment:** Docker + Render

## Setup

```powershell
# Clone the repo
git clone https://github.com/<your-username>/ai-resume-reviewer.git
cd ai-resume-reviewer

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run the app
uvicorn main:app --reload
```

Visit `http://localhost:8000/docs` for interactive API documentation.

## Status

Started: May 2026 — Active development.

## Author

Sangari B
