# 📄 AI Resume Reviewer

A full-stack web application that analyzes resumes (PDF), scores them against
best-practice rules, and shows what to improve — built with FastAPI and PostgreSQL.

## ✨ Features

- 🔐 **User authentication** — sign up / login with JWT tokens and bcrypt-hashed passwords
- 📤 **PDF upload & parsing** — extracts text, word/page/character counts
- 🎯 **Rule-based resume scoring** — scores 0–100 and lists strengths + improvements (no paid API)
- 👤 **Per-user data isolation** — each user only sees and manages their own resumes
- 💾 **Persistent storage** — resumes saved in PostgreSQL
- 🌐 **Clean frontend** — vanilla HTML/CSS/JS with client-side validation


## 🛠️ Tech Stack

| Layer    | Technology                          |
|----------|-------------------------------------|
| Backend  | Python, FastAPI, Uvicorn            |
| Database | PostgreSQL, SQLAlchemy ORM          |
| Auth     | JWT (python-jose), bcrypt           |
| PDF      | pdfplumber                          |
| Frontend | HTML, CSS, JavaScript (fetch API)   |

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/sangaribalasubramaniyen/ai-resume-reviewer.git
cd ai-resume-reviewer

2. Install dependencies
pip install -r requirements.txt

3. Set up environment variables
Copy .env.example to .env and fill in your values:
DATABASE_URL=postgresql://user:password@localhost:5432/resume_db
SECRET_KEY=your-secret-key

4. Run the server
python -m uvicorn main:app --reload

5. Open the frontend
Open frontend/login.html in your browser.

📚 API Endpoints

┌────────┬────────────────┬───────────────────────────────────┐
│ Method │    Endpoint    │            Description            │
├────────┼────────────────┼───────────────────────────────────┤
│ POST   │ /signup        │ Register a new user               │
├────────┼────────────────┼───────────────────────────────────┤
│ POST   │ /login         │ Log in, returns a JWT token       │
├────────┼────────────────┼───────────────────────────────────┤
│ POST   │ /upload-resume │ Upload a PDF and get its review   │
├────────┼────────────────┼───────────────────────────────────┤
│ GET    │ /resumes       │ List the logged-in user's resumes │
├────────┼────────────────┼───────────────────────────────────┤
│ DELETE │ /resumes/{id}  │ Delete one of your resumes        │
└────────┴────────────────┴───────────────────────────────────┘

🔒 Security Notes
- Passwords are hashed with bcrypt (never stored in plain text)
- All resume routes are scoped to the authenticated user (prevents IDOR)
- Secrets are kept in .env (gitignored), never committed

🗺️ Roadmap
- [ ] Weighted scoring rules
- [ ] Optional AI-powered analysis (Claude)
- [ ] Deploy to a live URL






