from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.analyzers.career_chat import CareerChatAssistant
from app.auth.session import get_current_user
from app.database import get_db
from app.github.client import GitHubAPIError
from app.models import ChatMessage, JobMatch, Resume, User
from app.services.developer_context import build_developer_context

router = APIRouter(prefix="/api/chat", tags=["AI Career Assistant Chat"])


class ChatRequest(BaseModel):
    message: str


def _serialize_message(message: ChatMessage) -> dict:
    return {
        "id": message.id,
        "role": message.role,
        "content": message.content,
        "timestamp": message.timestamp.isoformat() if message.timestamp else None,
    }


@router.get("")
def get_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == current_user.id)
        .order_by(ChatMessage.timestamp.asc())
        .limit(50)
        .all()
    )
    return [_serialize_message(message) for message in messages]


@router.post("")
async def chat_with_assistant(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        ctx = await build_developer_context(current_user, db)
    except GitHubAPIError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    user_message = ChatMessage(
        user_id=current_user.id,
        role="user",
        content=req.message,
        timestamp=datetime.utcnow(),
    )
    db.add(user_message)

    # Give the assistant the latest analyzed job as additional context.
    latest_match = (
        db.query(JobMatch)
        .filter(JobMatch.user_id == current_user.id)
        .order_by(JobMatch.calculated_at.desc())
        .first()
    )

    job_context = None
    if latest_match and latest_match.job_description:
        job = latest_match.job_description
        job_context = {
            "title": job.title,
            "company": job.company,
            "overall_match_score": latest_match.overall_match_score,
            "tech_score": latest_match.tech_score,
            "project_score": latest_match.project_score,
            "experience_score": latest_match.experience_score,
            "devops_score": latest_match.devops_score,
            "problem_solving_score": latest_match.problem_solving_score,
            "required_skills": job.required_skills or [],
            "preferred_skills": job.preferred_skills or [],
            "missing_skills": latest_match.missing_skills or [],
            "feedback_notes": latest_match.feedback_notes or [],
        }

    latest_resume = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.uploaded_at.desc())
        .first()
    )

    resume_context = None
    if latest_resume:
        resume_context = {
            "filename": latest_resume.filename,
            "mismatch_flags": latest_resume.mismatch_flags or [],
            "parsed": latest_resume.parsed_json or {},
        }

    assistant = CareerChatAssistant()
    reply = assistant.generate_response(
        req.message,
        ctx["profile"],
        ctx["repos"],
        ctx["analyses"],
        job_context=job_context,
        resume_context=resume_context,
    )

    assistant_message = ChatMessage(
        user_id=current_user.id,
        role="assistant",
        content=reply,
        timestamp=datetime.utcnow(),
    )
    db.add(assistant_message)
    db.commit()

    return {"query": req.message, "response": reply}
