from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from datetime import datetime
from dotenv import load_dotenv
import pdfplumber
import io

# Load variables from .env (like ANTHROPIC_API_KEY) into the environment.
# Must run BEFORE we import analyzer, because analyzer reads the key at import.
load_dotenv()

from analyzer import analyze_resume
import models
from database import engine, get_db

# Create the database tables (if they don't exist yet) when the app starts.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Resume Reviewer",
    description="An AI-powered resume analysis API using Claude",
    version="0.1.0",
)


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
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload a resume PDF and extract its text content."""

    extracted_text, page_count, file_size_kb = await _read_pdf(file)

    word_count = len(extracted_text.split())
    char_count = len(extracted_text)

     # Create a new Resume row and save it to PostgreSQL.
    resume = models.Resume(
        filename=file.filename,
        page_count=page_count,
        word_count=word_count,
        character_count=char_count,
        extracted_text=extracted_text,
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
def list_resumes(db: Session = Depends(get_db)):
    """Return all resumes saved in the database (newest first)."""
    resumes = db.query(models.Resume).order_by(models.Resume.uploaded_at.desc()).all()
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
