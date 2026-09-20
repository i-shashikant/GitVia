from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.session import get_current_user
from app.database import get_db
from app.models import User, Repository, DeveloperProfile
from app.analyzers.profile_analyzer import ProfileAnalyzer


router = APIRouter(
    prefix="/api/profile",
    tags=["Developer Profile"],
)


def build_profile_from_repositories(
    current_user: User,
    repositories: list[Repository],
):
    analyzed_repositories = []
    analyses = []

    for repository in repositories:
        analysis = {}

        if repository.metrics:
            analysis = (
                repository.metrics.analysis_json
                or {}
            )

        analyzed_repositories.append(
            {
                "id": repository.github_repo_id,
                "name": repository.name,
                "full_name": repository.full_name,
                "description": repository.description,
                "language": repository.language,
                "stars_count": repository.stars_count,
                "forks_count": repository.forks_count,
                "is_fork": repository.is_fork,
                "default_branch": repository.default_branch,
                "analysis": analysis,
            }
        )

        if analysis:
            analyses.append(analysis)

    analyzer = ProfileAnalyzer()

    result = analyzer.analyze_profile(
        analyzed_repositories,
        analyses,
    )

    return {
        "user": {
            "id": current_user.id,
            "github_id": current_user.github_id,
            "github_username": current_user.github_username,
            "name": current_user.name,
            "email": current_user.email,
            "avatar_url": current_user.avatar_url,
        },
        "repository_count": len(
            analyzed_repositories
        ),
        "profile": result,
    }


@router.get("")
def get_developer_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.access_token:
        raise HTTPException(
            status_code=401,
            detail="GitHub account is not connected",
        )

    repositories = (
        db.query(Repository)
        .filter(
            Repository.user_id == current_user.id
        )
        .all()
    )

    # No cached repositories yet.
    #
    # The frontend should load /api/repos first,
    # which performs the initial GitHub sync.
    if not repositories:
        raise HTTPException(
            status_code=404,
            detail="GitHub repositories have not been synced yet",
        )

    return build_profile_from_repositories(
        current_user,
        repositories,
    )