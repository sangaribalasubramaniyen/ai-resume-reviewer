from fastapi import FastAPI
from datetime import datetime

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
