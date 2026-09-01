import os

import jwt
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")

if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET is not configured")


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


@router.get("/me")
def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
):
    session_token = request.cookies.get("gitvia_session")

    if not session_token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
        )

    try:
        payload = jwt.decode(
            session_token,
            JWT_SECRET,
            algorithms=["HS256"],
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session",
        )

    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid session",
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return {
        "id": user.id,
        "github_id": user.github_id,
        "github_username": user.github_username,
        "name": user.name,
        "email": user.email,
        "avatar_url": user.avatar_url,
    }