from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.session import get_current_user
from app.models import User
from app.github.client import GitHubAPIError
from app.services.developer_context import build_developer_context
from app.analyzers.roadmap_generator import RoadmapGenerator

router = APIRouter(prefix="/api/roadmap", tags=["Personalized Learning Roadmap"])


@router.get("")
async def get_roadmap(
    target_role: str = "Backend Engineer",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        ctx = await build_developer_context(current_user)
    except GitHubAPIError as exc:
        raise HTTPException(status_code=401, detail=str(exc))

    generator = RoadmapGenerator()
    return generator.generate_roadmap(ctx["profile"], ctx["repos"], target_role)