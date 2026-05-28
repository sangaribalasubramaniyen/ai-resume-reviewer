from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
import pdfplumber
import io

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


@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """Upload a resume PDF and extract its text content."""

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

    word_count = len(extracted_text.split())
    char_count = len(extracted_text)

    return JSONResponse({
        "filename": file.filename,
        "file_size_kb": file_size_kb,
        "page_count": page_count,
        "word_count": word_count,
        "character_count": char_count,
        "preview": extracted_text[:500] + ("..." if len(extracted_text) > 500 else ""),
        "full_text": extracted_text,
    })
