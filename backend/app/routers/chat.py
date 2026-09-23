from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.analyzers.career_chat import CareerChatAssistant
from app.auth.session import get_current_user
from app.database import get_db
from app.github.client import GitHubAPIError
from app.models import ChatMessage, User
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

    assistant = CareerChatAssistant()
    reply = assistant.generate_response(
        req.message,
        ctx["profile"],
        ctx["repos"],
        ctx["analyses"],
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
