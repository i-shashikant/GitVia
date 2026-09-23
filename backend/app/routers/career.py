from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.session import get_current_user
from app.models import User
from app.github.client import GitHubAPIError
from app.services.developer_context import build_developer_context
from app.analyzers.resume_analyzer import ResumeAnalyzer
from app.analyzers.job_analyzer import JobAnalyzer

router = APIRouter(prefix="/api/career", tags=["Career Intelligence & Matching"])


class JobAnalyzeRequest(BaseModel):
    title: str = "Amazon SDE Intern"
    company: str = "Amazon"
    job_text: str


@router.post("/resume/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    contents = await file.read()
    analyzer = ResumeAnalyzer()
    raw_text = analyzer.extract_text_from_pdf(contents)

    try:
        ctx = await build_developer_context(current_user)
    except GitHubAPIError as exc:
        raise HTTPException(status_code=401, detail=str(exc))

    analysis = analyzer.analyze_resume(raw_text, ctx["repos"])

    return {
        "filename": file.filename,
        "raw_text_length": len(raw_text),
        "parsed_skills": analysis["parsed_skills"],
        "education": analysis["education"],
        "experience": analysis["experience"],
        "mismatch_flags": analysis["mismatch_flags"],
        "bullets_suggestions": analysis["bullets_suggestions"],
    }


@router.post("/jobs/analyze")
async def analyze_job_description(
    req: JobAnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        ctx = await build_developer_context(current_user)
    except GitHubAPIError as exc:
        raise HTTPException(status_code=401, detail=str(exc))

    job_analyzer = JobAnalyzer()
    return job_analyzer.analyze_job(req.title, req.company, req.job_text, ctx["profile"])