from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.analyzers.roadmap_generator import RoadmapGenerator
from app.auth.session import get_current_user
from app.database import get_db
from app.github.client import GitHubAPIError
from app.models import JobMatch, Roadmap, SkillGap, User
from app.services.developer_context import build_developer_context

router = APIRouter(prefix="/api/roadmap", tags=["Personalized Learning Roadmap"])


@router.get("")
async def get_roadmap(
    target_role: str = "Backend Engineer",
    refresh: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not refresh:
        existing = (
            db.query(Roadmap)
            .filter(
                Roadmap.user_id == current_user.id,
                Roadmap.target_role == target_role,
            )
            .order_by(Roadmap.created_at.desc())
            .first()
        )
        if existing and existing.weekly_tasks:
            return existing.weekly_tasks

    try:
        ctx = await build_developer_context(current_user, db)
    except GitHubAPIError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    generator = RoadmapGenerator()
    result = generator.generate_roadmap(ctx["profile"], ctx["repos"], target_role)

    roadmap = Roadmap(
        user_id=current_user.id,
        target_role=target_role,
        duration_weeks=result.get("duration_weeks") or 6,
        weekly_tasks=result,
        created_at=datetime.utcnow(),
    )
    db.add(roadmap)
    db.commit()
    return result
