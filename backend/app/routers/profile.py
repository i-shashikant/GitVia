from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth.session import get_current_user
from app.database import get_db
from app.github.client import GitHubAPIError
from app.models import User
from app.services.analysis import get_developer_context, profile_payload

router = APIRouter(
    prefix="/api/profile",
    tags=["Developer Profile"],
)


@router.get("")
async def get_developer_profile(
    refresh: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        ctx = await get_developer_context(db, current_user, refresh=refresh)
    except GitHubAPIError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    payload = profile_payload(
        current_user,
        ctx["profile"],
        len(ctx["serialized_repos"]),
    )
    payload["from_cache"] = ctx.get("from_cache", False)
    return payload
