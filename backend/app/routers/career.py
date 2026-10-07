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
        ctx["repos"],
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
        overall_match_score=result.get("overall_match_score", 0),
        tech_score=result.get("tech_score", 0),
        project_score=result.get("project_score", 0),
        experience_score=result.get("experience_score", 0),
        devops_score=result.get("devops_score", 0),
        problem_solving_score=result.get("problem_solving_score", 0),
        missing_skills=result.get("missing_skills") or [],
        feedback_notes=result.get("feedback_notes") or [],
        calculated_at=datetime.utcnow(),
    )
    db.add(match)

    skill_gaps = result.get("skill_gaps") or {}

    gap = SkillGap(
        user_id=current_user.id,
        target_role=req.title,
        strong_skills=skill_gaps.get("strong") or [],
        improving_skills=(
            skill_gaps.get("improving")
            or skill_gaps.get("weak")
            or []
        ),
        missing_skills=skill_gaps.get("missing") or [],
    )
    result["skill_gaps"]["improving"] = (
        result["skill_gaps"].get("improving")
        or result["skill_gaps"].get("weak")
        or []
    )
    db.add(gap)
    db.commit()

    result["job_id"] = job.id
    result["match_id"] = match.id
    return result


@router.get("/jobs/history")
def get_job_analysis_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    matches = (
        db.query(JobMatch)
        .filter(JobMatch.user_id == current_user.id)
        .order_by(JobMatch.calculated_at.desc())
        .limit(20)
        .all()
    )

    history = []

    for match in matches:
        job = match.job_description
        skill_gap = (
            db.query(SkillGap)
            .filter(
                SkillGap.user_id == current_user.id,
                SkillGap.target_role == job.title,
                SkillGap.created_at <= match.calculated_at,
            )
            .order_by(SkillGap.created_at.desc())
            .first()
        )

        history.append({
            "job_id": job.id,
            "match_id": match.id,

            # Original job information
            "title": job.title,
            "company": job.company or "Unknown Company",
            "job_text": job.raw_text or "",

            # Match scores
            "overall_match_score": match.overall_match_score,
            "tech_score": match.tech_score,
            "project_score": match.project_score,
            "experience_score": match.experience_score,
            "devops_score": match.devops_score,
            "problem_solving_score": match.problem_solving_score,

            # Extracted requirements
            "required_skills": job.required_skills or [],
            "preferred_skills": job.preferred_skills or [],

            # Match gaps
            "missing_skills": match.missing_skills or [],
            "feedback_notes": match.feedback_notes or [],

            # Skill-gap snapshot
            "strong_skills": skill_gap.strong_skills if skill_gap else [],
            "improving_skills": (
                skill_gap.improving_skills
                if skill_gap
                else []
            ),
            "skill_gap_missing_skills": (
                skill_gap.missing_skills
                if skill_gap
                else match.missing_skills or []
            ),

            "calculated_at": (
                match.calculated_at.isoformat()
                if match.calculated_at
                else None
            ),
        })

    return {
        "history": history,
        "count": len(history),
    }

@router.delete("/jobs/{job_id}")
def delete_job_analysis(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = (
        db.query(JobDescription)
        .filter(
            JobDescription.id == job_id,
            JobDescription.user_id == current_user.id,
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job analysis not found.",
        )

    # Delete all matches belonging to this job first.
    db.query(JobMatch).filter(
        JobMatch.job_id == job.id,
        JobMatch.user_id == current_user.id,
    ).delete(synchronize_session=False)

    # Delete the job itself.
    db.delete(job)

    db.commit()

    return {
        "success": True,
        "job_id": job_id,
    }