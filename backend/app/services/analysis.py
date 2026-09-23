from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.analyzers.profile_analyzer import ProfileAnalyzer
from app.analyzers.repo_analyzer import RepositoryAnalyzer
from app.config import get_settings
from app.github.client import GitHubAPIError, GitHubClient
from app.models import (
    DeveloperProfile,
    GitHubProfile,
    Repository,
    RepositoryMetric,
    User,
)
from app.security.crypto import decrypt_token

logger = logging.getLogger(__name__)


def serialize_repository(repository: Repository) -> dict[str, Any]:
    metric = repository.metrics
    analysis = metric.analysis_json if metric and metric.analysis_json else {}

    return {
        "id": repository.github_repo_id,
        "github_repo_id": repository.github_repo_id,
        "name": repository.name,
        "full_name": repository.full_name,
        "description": repository.description,
        "language": repository.language,
        "stars_count": repository.stars_count,
        "forks_count": repository.forks_count,
        "html_url": f"https://github.com/{repository.full_name}",
        "default_branch": repository.default_branch,
        "is_fork": repository.is_fork,
        "quality_score": metric.overall_score if metric else 0,
        "tech_stack": repository.tech_stack or analysis.get("tech_stack") or [],
        "analysis": analysis,
        "cached": True,
        "updated_at": (
            repository.updated_at.isoformat() if repository.updated_at else None
        ),
    }


def serialize_user(user: User) -> dict[str, Any]:
    return {
        "id": user.id,
        "github_id": user.github_id,
        "github_username": user.github_username,
        "name": user.name,
        "email": user.email,
        "avatar_url": user.avatar_url,
    }


def profile_payload(user: User, profile: dict[str, Any], repo_count: int) -> dict[str, Any]:
    return {
        "user": serialize_user(user),
        "repository_count": repo_count,
        "profile": profile,
    }


def _has_cached_analysis(db: Session, user: User) -> bool:
    repo_count = (
        db.query(Repository)
        .filter(Repository.user_id == user.id)
        .count()
    )
    profile = (
        db.query(DeveloperProfile)
        .filter(DeveloperProfile.user_id == user.id)
        .first()
    )
    return bool(repo_count and profile)


def _profile_from_row(row: DeveloperProfile) -> dict[str, Any]:
    return {
        "primary_role": row.primary_role,
        "secondary_role": row.secondary_role,
        "current_level": row.current_level,
        "portfolio_score": row.portfolio_score,
        "github_score": row.github_score,
        "readiness_score": row.readiness_score,
        "dimension_averages": (row.skill_scores or {}).get("_dimension_averages")
        if isinstance(row.skill_scores, dict) and "_dimension_averages" in (row.skill_scores or {})
        else {
            "projects": row.github_score,
            "github": row.github_score,
            "documentation": 0,
            "testing": 0,
            "devops": 0,
            "scalability": 0,
        },
        "skill_scores": {
            key: value
            for key, value in (row.skill_scores or {}).items()
            if not str(key).startswith("_")
        },
        "strongest_skills": row.strongest_skills or [],
        "weakest_skills": row.weakest_skills or [],
        "top_recommendations": (row.skill_scores or {}).get("_recommendations", [])
        if isinstance(row.skill_scores, dict)
        else [],
    }


def _store_profile(profile: dict[str, Any], row: DeveloperProfile) -> None:
    row.primary_role = profile.get("primary_role") or "Software Developer"
    row.secondary_role = profile.get("secondary_role")
    row.current_level = profile.get("current_level") or "Developing"
    row.strongest_skills = profile.get("strongest_skills") or []
    row.weakest_skills = profile.get("weakest_skills") or []
    scores = dict(profile.get("skill_scores") or {})
    scores["_dimension_averages"] = profile.get("dimension_averages") or {}
    scores["_recommendations"] = profile.get("top_recommendations") or []
    row.skill_scores = scores
    row.portfolio_score = float(profile.get("portfolio_score") or 0)
    row.github_score = float(profile.get("github_score") or 0)
    row.readiness_score = float(profile.get("readiness_score") or 0)
    row.analyzed_at = datetime.utcnow()


async def _analyze_single_repository(
    client: GitHubClient,
    analyzer: RepositoryAnalyzer,
    repo: dict[str, Any],
    semaphore: asyncio.Semaphore,
) -> dict[str, Any] | None:
    owner_data = repo.get("owner") or {}
    owner = owner_data.get("login")
    name = repo.get("name")

    if not owner or not name:
        return None

    branch = repo.get("default_branch") or "main"

    async with semaphore:
        try:
            readme = await asyncio.wait_for(
                client.get_repo_readme(owner, name),
                timeout=45,
            )
            paths = await asyncio.wait_for(
                client.get_repo_tree(owner, name, branch),
                timeout=45,
            )
        except (asyncio.TimeoutError, GitHubAPIError) as exc:
            logger.warning("Skipping %s/%s: %s", owner, name, exc)
            return None

    analysis = analyzer.analyze_repo(
        name=name,
        readme=readme,
        paths=paths,
        language=repo.get("language"),
        stars=repo.get("stargazers_count", 0),
        forks=repo.get("forks_count", 0),
    )

    return {
        "github_repo": repo,
        "readme": readme,
        "paths": paths,
        "analysis": analysis,
    }


def save_repository_analysis(db: Session, user: User, item: dict[str, Any]) -> Repository:
    repo = item["github_repo"]
    analysis = item["analysis"]

    existing = (
        db.query(Repository)
        .filter(
            Repository.user_id == user.id,
            Repository.github_repo_id == repo["id"],
        )
        .first()
    )

    if not existing:
        existing = Repository(
            user_id=user.id,
            github_repo_id=repo["id"],
        )
        db.add(existing)

    existing.name = repo["name"]
    existing.full_name = repo["full_name"]
    existing.description = repo.get("description")
    existing.language = repo.get("language")
    existing.stars_count = repo.get("stargazers_count", 0)
    existing.forks_count = repo.get("forks_count", 0)
    existing.is_fork = repo.get("fork", False)
    existing.default_branch = repo.get("default_branch") or "main"
    existing.readme_content = item["readme"]
    existing.file_tree_json = item["paths"]
    existing.tech_stack = analysis.get("tech_stack") or []
    existing.updated_at = datetime.utcnow()
    db.flush()

    metric = (
        db.query(RepositoryMetric)
        .filter(RepositoryMetric.repo_id == existing.id)
        .first()
    )
    if not metric:
        metric = RepositoryMetric(repo_id=existing.id)
        db.add(metric)

    metric.overall_score = analysis.get("overall_score", 0)
    metric.documentation_score = analysis.get("documentation", {}).get("score", 0)
    metric.architecture_score = analysis.get("architecture", {}).get("score", 0)
    metric.code_quality_score = analysis.get("code_quality", {}).get("score", 0)
    metric.testing_score = analysis.get("testing", {}).get("score", 0)
    metric.devops_score = analysis.get("devops", {}).get("score", 0)
    metric.scalability_score = analysis.get("scalability", {}).get("score", 0)
    metric.analysis_json = analysis
    metric.analyzed_at = datetime.utcnow()
    return existing


def _context_from_db(db: Session, user: User) -> dict[str, Any]:
    repositories = (
        db.query(Repository)
        .filter(Repository.user_id == user.id)
        .all()
    )
    serialized = [serialize_repository(repo) for repo in repositories]
    analyses = [item.get("analysis") or {} for item in serialized]
    github_like = [
        {
            "name": item["name"],
            "language": item["language"],
            "description": item["description"],
            "tech_stack": item.get("tech_stack") or [],
            "quality_score": item.get("quality_score") or 0,
            "analysis": item.get("analysis") or {},
        }
        for item in serialized
    ]

    profile_row = (
        db.query(DeveloperProfile)
        .filter(DeveloperProfile.user_id == user.id)
        .first()
    )
    if profile_row:
        profile = _profile_from_row(profile_row)
    else:
        profile = ProfileAnalyzer().analyze_profile(github_like, analyses)

    return {
        "repos": github_like,
        "analyses": analyses,
        "profile": profile,
        "serialized_repos": serialized,
        "from_cache": True,
    }


async def refresh_user_analysis(db: Session, user: User) -> dict[str, Any]:
    token = decrypt_token(user.access_token)
    if not token:
        raise GitHubAPIError("GitHub account is not connected")

    settings = get_settings()
    client = GitHubClient(token)
    analyzer = RepositoryAnalyzer()
    github_repos = await asyncio.wait_for(client.get_user_repos(), timeout=60)

    semaphore = asyncio.Semaphore(max(1, settings.analysis_concurrency))
    tasks = [
        _analyze_single_repository(client, analyzer, repo, semaphore)
        for repo in github_repos
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    analyzed = []
    for result in results:
        if isinstance(result, Exception) or result is None:
            if isinstance(result, Exception):
                logger.warning("Repo analysis failed: %s", result)
            continue
        analyzed.append(result)

    saved = [save_repository_analysis(db, user, item) for item in analyzed]

    github_like = []
    analyses = []
    for item in analyzed:
        repo = item["github_repo"]
        analysis = item["analysis"]
        analyses.append(analysis)
        github_like.append(
            {
                "name": repo.get("name"),
                "language": repo.get("language"),
                "description": repo.get("description"),
                "tech_stack": analysis.get("tech_stack") or [],
                "quality_score": analysis.get("overall_score") or 0,
                "analysis": analysis,
            }
        )

    profile = ProfileAnalyzer().analyze_profile(github_like, analyses)

    profile_row = (
        db.query(DeveloperProfile)
        .filter(DeveloperProfile.user_id == user.id)
        .first()
    )
    if not profile_row:
        profile_row = DeveloperProfile(user_id=user.id)
        db.add(profile_row)
    _store_profile(profile, profile_row)

    github_profile = (
        db.query(GitHubProfile)
        .filter(GitHubProfile.user_id == user.id)
        .first()
    )
    if not github_profile:
        github_profile = GitHubProfile(user_id=user.id)
        db.add(github_profile)
    github_profile.public_repos = len(github_repos)
    github_profile.overall_score = float(profile.get("github_score") or 0)
    github_profile.updated_at = datetime.utcnow()

    db.commit()

    return {
        "repos": github_like,
        "analyses": analyses,
        "profile": profile,
        "serialized_repos": [serialize_repository(repo) for repo in saved],
        "from_cache": False,
    }


async def get_developer_context(
    db: Session,
    user: User,
    refresh: bool = False,
) -> dict[str, Any]:
    if not refresh and _has_cached_analysis(db, user):
        logger.info("Using cached analysis for user %s", user.id)
        return _context_from_db(db, user)

    logger.info("Refreshing GitHub analysis for user %s", user.id)
    return await refresh_user_analysis(db, user)
