from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from datetime import datetime
from dotenv import load_dotenv
import pdfplumber
import io
from pydantic import BaseModel
from auth import hash_password, verify_password, create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from auth import get_current_user


# Load variables from .env (like ANTHROPIC_API_KEY) into the environment.
# Must run BEFORE we import analyzer, because analyzer reads the key at import.
load_dotenv()

from analyzer import analyze_resume
from analyze import analyze_resume_text
import models
from database import engine, get_db

# Create the database tables (if they don't exist yet) when the app starts.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Resume Reviewer",
    description="An AI-powered resume analysis API using Claude",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # "*" = any origin (fine for learning; lock down in production)
    allow_credentials=True,
    allow_methods=["*"],      # allow GET, POST, PUT, DELETE...
    allow_headers=["*"],      # allow Authorization, Content-Type...
  )

class UserCreate(BaseModel):
    email: str
    password: str



@app.get("/")
def read_root():
    return {
        "app": "AI Resume Reviewer",
        "status": "running",
        "message": "Welcome! Visit /docs for API documentation.",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }


async def _read_pdf(file: UploadFile):
    """
    Helper: validate an uploaded PDF and return (extracted_text, page_count, file_size_kb).

    Shared by /upload-resume and /analyze-resume so we don't repeat this
    logic in two places (DRY principle).
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    contents = await file.read()
    file_size_kb = round(len(contents) / 1024, 2)

    if file_size_kb > 5120:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 5 MB."
        )

    extracted_text = ""
    page_count = 0

    try:
        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            page_count = len(pdf.pages)
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read PDF: {str(e)}"
        )

    return extracted_text, page_count, file_size_kb


@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db),current_user: models.User = Depends(get_current_user),):
    """Upload a resume PDF and extract its text content."""

    extracted_text, page_count, file_size_kb = await _read_pdf(file)

    word_count = len(extracted_text.split())
    char_count = len(extracted_text)
    review = analyze_resume_text(extracted_text)
     # Create a new Resume row and save it to PostgreSQL.
    resume = models.Resume(
        filename=file.filename,
        page_count=page_count,
        word_count=word_count,
        character_count=char_count,
        extracted_text=extracted_text,
        user_id=current_user.id,
    )
    db.add(resume)        # stage the new row
    db.commit()           # actually write it to the database
    db.refresh(resume)    # reload it to get the auto-generated id

    return JSONResponse({
        "filename": file.filename,
        "file_size_kb": file_size_kb,
        "page_count": page_count,
        "word_count": word_count,
        "character_count": char_count,
        "preview": extracted_text[:500] + ("..." if len(extracted_text) > 500 else ""),
        "full_text": extracted_text,
        "review": review, 
    })


@app.post("/analyze-resume")
async def analyze_resume_endpoint(file: UploadFile = File(...)):
    """
    Upload a resume PDF, extract the text, then send it to Claude
    for AI-powered analysis (ATS score, strengths, weaknesses, suggestions).
    """
    extracted_text, page_count, file_size_kb = await _read_pdf(file)

    # Guard: an empty/scanned PDF has no text to analyze.
    if len(extracted_text.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Could not extract enough text. Is this a scanned image PDF?"
        )

    try:
        feedback = analyze_resume(extracted_text)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"AI analysis failed: {str(e)}"
        )

    return JSONResponse({
        "filename": file.filename,
        "page_count": page_count,
        "analysis": feedback,
    })


@app.get("/resumes")
def list_resumes(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
      """Return only the logged-in user's resumes (newest first)."""
      resumes = (
          db.query(models.Resume)
          .filter(models.Resume.user_id == current_user.id)   # ← only THIS user's rows
          .order_by(models.Resume.uploaded_at.desc())
          .all()
      )
      return [
          {
              "id": r.id,
              "filename": r.filename,
              "page_count": r.page_count,
              "word_count": r.word_count,
              "uploaded_at": r.uploaded_at.isoformat() if r.uploaded_at else None,
          }
          for r in resumes
      ]

@app.get("/resumes/{resume_id}")
def get_resume(resume_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
      """Get ONE resume — only if it belongs to the logged-in user."""
      resume = (
          db.query(models.Resume)
          .filter(models.Resume.id == resume_id, models.Resume.user_id == current_user.id)
          .first()
      )
      if resume is None:
          raise HTTPException(status_code=404, detail="Resume not found")
      return {
          "id": resume.id,
          "filename": resume.filename,
          "page_count": resume.page_count,
          "word_count": resume.word_count,
          "character_count": resume.character_count,
          "extracted_text": resume.extracted_text,
          "uploaded_at": resume.uploaded_at.isoformat() if resume.uploaded_at else None,
      }

def delete_resume(resume_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
      """Delete ONE resume — only if it belongs to the logged-in user."""
      resume = (
          db.query(models.Resume)
          .filter(models.Resume.id == resume_id, models.Resume.user_id == current_user.id)
          .first()
      )
      if resume is None:
          raise HTTPException(status_code=404, detail="Resume not found")

      db.delete(resume)
      db.commit()
      return {"message": f"Resume {resume_id} deleted successfully"}



@app.put("/resumes/{resume_id}")
async def update_resume(resume_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.User =
  Depends(get_current_user)):
      """Replace an existing resume — only if it belongs to the logged-in user."""
      resume = (
          db.query(models.Resume)
          .filter(models.Resume.id == resume_id, models.Resume.user_id == current_user.id)
          .first()
      )
      if resume is None:
          raise HTTPException(status_code=404, detail="Resume not found")

      extracted_text, page_count, file_size_kb = await _read_pdf(file)

      resume.filename = file.filename
      resume.page_count = page_count
      resume.word_count = len(extracted_text.split())
      resume.character_count = len(extracted_text)
      resume.extracted_text = extracted_text
      resume.uploaded_at = datetime.utcnow()

      db.commit()
      db.refresh(resume)

      return {
          "message": f"Resume {resume_id} updated successfully",
          "id": resume.id,
          "filename": resume.filename,
          "page_count": resume.page_count,
          "word_count": resume.word_count,
      }

@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user with a hashed password."""
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = models.User(
        email=user.email,
        hashed_password=hash_password(user.password),   # store the HASH, not the password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created", "id": new_user.id, "email": new_user.email}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Check credentials and return a JWT token if valid."""
    db_user = db.query(models.User).filter(models.User.email == form_data.username).first()

    if db_user is None or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(data={"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}