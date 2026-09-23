from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth.session import get_current_user
from app.database import get_db
from app.github.client import GitHubAPIError
from app.models import Repository, User
from app.services.analysis import get_developer_context, serialize_repository

router = APIRouter(
    prefix="/api/repos",
    tags=["Repositories & Code Quality"],
)


@router.get("")
async def list_repositories(
    refresh: bool = Query(False, description="Force a fresh GitHub analysis"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        ctx = await get_developer_context(db, current_user, refresh=refresh)
    except GitHubAPIError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return ctx["serialized_repos"]


@router.get("/{repo_id}")
async def get_repository(
    repo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repository = (
        db.query(Repository)
        .filter(
            Repository.user_id == current_user.id,
            Repository.github_repo_id == repo_id,
        )
        .first()
    )

    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")

    return serialize_repository(repository)
