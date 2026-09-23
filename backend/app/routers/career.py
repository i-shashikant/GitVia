from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.analyzers.job_analyzer import JobAnalyzer
from app.analyzers.resume_analyzer import ResumeAnalyzer
from app.auth.session import get_current_user
from app.database import get_db
from app.github.client import GitHubAPIError
from app.models import JobDescription, JobMatch, Resume, SkillGap, User
from app.services.developer_context import build_developer_context

router = APIRouter(prefix="/api/career", tags=["Career Intelligence & Matching"])


class JobAnalyzeRequest(BaseModel):
    title: str = "Software Engineer Intern"
    company: str = ""
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
        ctx = await build_developer_context(current_user, db)
    except GitHubAPIError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    analysis = analyzer.analyze_resume(raw_text, ctx["repos"])

    resume = Resume(
        user_id=current_user.id,
        filename=file.filename or "resume.pdf",
        raw_text=raw_text,
        parsed_json={
            "parsed_skills": analysis["parsed_skills"],
            "education": analysis["education"],
            "experience": analysis["experience"],
            "bullets_suggestions": analysis["bullets_suggestions"],
        },
        mismatch_flags=analysis["mismatch_flags"],
        uploaded_at=datetime.utcnow(),
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return {
        "id": resume.id,
        "filename": resume.filename,
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
        ctx = await build_developer_context(current_user, db)
    except GitHubAPIError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    job_analyzer = JobAnalyzer()
    result = job_analyzer.analyze_job(
        req.title,
        req.company,
        req.job_text,
        ctx["profile"],
    )

    job = JobDescription(
        user_id=current_user.id,
        title=req.title,
        company=req.company or None,
        raw_text=req.job_text,
        required_skills=result.get("required_skills") or [],
        preferred_skills=result.get("preferred_skills") or [],
    )
    db.add(job)
    db.flush()

    match = JobMatch(
        user_id=current_user.id,
        job_id=job.id,
        overall_match_score=result.get("match_score") or 0,
        tech_score=result.get("score_breakdown", {}).get("technical_skills", 0),
        project_score=result.get("score_breakdown", {}).get("projects", 0),
        experience_score=result.get("score_breakdown", {}).get("experience", 0),
        devops_score=result.get("score_breakdown", {}).get("devops", 0),
        problem_solving_score=result.get("score_breakdown", {}).get("problem_solving", 0),
        missing_skills=result.get("skill_gaps", {}).get("missing") or [],
        feedback_notes=result.get("missing_evidence_notes") or [],
        calculated_at=datetime.utcnow(),
    )
    db.add(match)

    gap = SkillGap(
        user_id=current_user.id,
        target_role=req.title,
        strong_skills=result.get("skill_gaps", {}).get("strong") or [],
        improving_skills=result.get("skill_gaps", {}).get("improving") or [],
        missing_skills=result.get("skill_gaps", {}).get("missing") or [],
    )
    db.add(gap)
    db.commit()

    result["job_id"] = job.id
    result["match_id"] = match.id
    return result
