from __future__ import annotations

import asyncio
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth.session import get_current_user
from app.database import get_db
from app.github.client import GitHubAPIError, GitHubClient
from app.models import Repository, RepositoryMetric, User
from app.analyzers.repo_analyzer import RepositoryAnalyzer


router = APIRouter(
    prefix="/api/repos",
    tags=["Repositories & Code Quality"],
)


def serialize_repository(repository: Repository) -> dict:
    metric = repository.metrics

    analysis = (
        metric.analysis_json
        if metric and metric.analysis_json
        else {}
    )

    return {
        "id": repository.github_repo_id,
        "name": repository.name,
        "full_name": repository.full_name,
        "description": repository.description,
        "language": repository.language,
        "stars_count": repository.stars_count,
        "forks_count": repository.forks_count,
        "html_url": f"https://github.com/{repository.full_name}",
        "default_branch": repository.default_branch,
        "is_fork": repository.is_fork,
        "quality_score": (
            metric.overall_score
            if metric
            else 0
        ),
        "analysis": analysis,
        "cached": True,
        "updated_at": (
            repository.updated_at.isoformat()
            if repository.updated_at
            else None
        ),
    }


async def analyze_single_repository(
    client: GitHubClient,
    analyzer: RepositoryAnalyzer,
    repo: dict,
):
    owner = repo["owner"]["login"]
    name = repo["name"]
    branch = repo.get("default_branch") or "main"

    readme_task = client.get_repo_readme(
        owner,
        name,
    )

    tree_task = client.get_repo_tree(
        owner,
        name,
        branch,
    )

    readme, paths = await asyncio.gather(
        readme_task,
        tree_task,
    )

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


async def analyze_repositories(
    client: GitHubClient,
    github_repos: list[dict],
):
    analyzer = RepositoryAnalyzer()

    tasks = [
        analyze_single_repository(
            client,
            analyzer,
            repo,
        )
        for repo in github_repos
    ]

    results = await asyncio.gather(
        *tasks,
        return_exceptions=True,
    )

    successful = []

    for result in results:
        if isinstance(result, Exception):
            continue

        successful.append(result)

    return successful


def save_repository_analysis(
    db: Session,
    user: User,
    item: dict,
):
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
    existing.stars_count = repo.get(
        "stargazers_count",
        0,
    )
    existing.forks_count = repo.get(
        "forks_count",
        0,
    )
    existing.is_fork = repo.get(
        "fork",
        False,
    )
    existing.default_branch = (
        repo.get("default_branch")
        or "main"
    )
    existing.readme_content = item["readme"]
    existing.file_tree_json = item["paths"]

    db.flush()

    metric = (
        db.query(RepositoryMetric)
        .filter(
            RepositoryMetric.repo_id == existing.id
        )
        .first()
    )

    if not metric:
        metric = RepositoryMetric(
            repo_id=existing.id
        )
        db.add(metric)

    metric.overall_score = analysis.get(
        "overall_score",
        0,
    )

    metric.documentation_score = analysis.get(
        "documentation",
        {},
    ).get("score", 0)

    metric.architecture_score = analysis.get(
        "architecture",
        {},
    ).get("score", 0)

    metric.code_quality_score = analysis.get(
        "code_quality",
        {},
    ).get("score", 0)

    metric.testing_score = analysis.get(
        "testing",
        {},
    ).get("score", 0)

    metric.devops_score = analysis.get(
        "devops",
        {},
    ).get("score", 0)

    metric.scalability_score = analysis.get(
        "scalability",
        {},
    ).get("score", 0)

    metric.analysis_json = analysis
    metric.analyzed_at = datetime.utcnow()

    return existing


@router.get("")
async def list_repositories(
    refresh: bool = Query(
        False,
        description="Force a fresh GitHub analysis",
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.access_token:
        raise HTTPException(
            status_code=401,
            detail="GitHub account is not connected",
        )

    # ---------------------------------------------------------
    # FAST PATH
    # ---------------------------------------------------------
    #
    # If repositories already exist in PostgreSQL and the user
    # did not explicitly request refresh, return cached data.
    #
    # This is what makes dashboard refreshes fast.
    # ---------------------------------------------------------

    cached_repositories = (
        db.query(Repository)
        .filter(
            Repository.user_id == current_user.id
        )
        .all()
    )

    if cached_repositories and not refresh:
        return [
            serialize_repository(repo)
            for repo in cached_repositories
        ]

    # ---------------------------------------------------------
    # FRESH GITHUB ANALYSIS
    # ---------------------------------------------------------

    client = GitHubClient(
        current_user.access_token
    )

    try:
        github_repos = await client.get_user_repos()
    except GitHubAPIError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        )

    analyzed = await analyze_repositories(
        client,
        github_repos,
    )

    results = []

    for item in analyzed:
        repository = save_repository_analysis(
            db,
            current_user,
            item,
        )

        results.append(
            repository
        )

    db.commit()

    return [
        serialize_repository(repo)
        for repo in results
    ]


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
        raise HTTPException(
            status_code=404,
            detail="Repository not found",
        )

    return serialize_repository(
        repository
    )