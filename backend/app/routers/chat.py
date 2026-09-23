from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.session import get_current_user
from app.models import User
from app.github.client import GitHubAPIError
from app.services.developer_context import build_developer_context
from app.analyzers.career_chat import CareerChatAssistant

router = APIRouter(prefix="/api/chat", tags=["AI Career Assistant Chat"])


class ChatRequest(BaseModel):
    message: str


@router.post("")
async def chat_with_assistant(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        ctx = await build_developer_context(current_user)
    except GitHubAPIError as exc:
        raise HTTPException(status_code=401, detail=str(exc))

    assistant = CareerChatAssistant()
    reply = assistant.generate_response(
        req.message,
        ctx["profile"],
        ctx["repos"],
        ctx["analyses"],
    )

    return {"query": req.message, "response": reply}