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


# ============================================================
# SERIALIZATION
# ============================================================

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
        "html_url": (
            f"https://github.com/{repository.full_name}"
        ),
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


# ============================================================
# SINGLE REPOSITORY ANALYSIS
# ============================================================

async def analyze_single_repository(
    client: GitHubClient,
    analyzer: RepositoryAnalyzer,
    repo: dict,
):

    owner_data = repo.get("owner") or {}

    owner = owner_data.get("login")
    name = repo.get("name")

    if not owner or not name:
        print(
            "[GitVia] Skipping malformed repository."
        )
        return None

    branch = (
        repo.get("default_branch")
        or "main"
    )

    full_name = f"{owner}/{name}"

    print(
        f"[GitVia] START → {full_name}"
    )

    try:

        # ----------------------------------------------------
        # Fetch README
        # ----------------------------------------------------

        print(
            f"[GitVia] {full_name} → fetching README..."
        )

        readme = await asyncio.wait_for(
            client.get_repo_readme(
                owner,
                name,
            ),
            timeout=45,
        )

        # ----------------------------------------------------
        # Fetch repository tree
        # ----------------------------------------------------

        print(
            f"[GitVia] {full_name} → fetching tree..."
        )

        paths = await asyncio.wait_for(
            client.get_repo_tree(
                owner,
                name,
                branch,
            ),
            timeout=45,
        )

        print(
            f"[GitVia] {full_name} → "
            f"tree received ({len(paths)} paths)"
        )

        # ----------------------------------------------------
        # Run analyzer
        # ----------------------------------------------------

        print(
            f"[GitVia] {full_name} → analyzing..."
        )

        analysis = analyzer.analyze_repo(
            name=name,
            readme=readme,
            paths=paths,
            language=repo.get("language"),
            stars=repo.get(
                "stargazers_count",
                0,
            ),
            forks=repo.get(
                "forks_count",
                0,
            ),
        )

        score = analysis.get(
            "overall_score",
            0,
        )

        print(
            f"[GitVia] SUCCESS → "
            f"{full_name} = {score}"
        )

        return {
            "github_repo": repo,
            "readme": readme,
            "paths": paths,
            "analysis": analysis,
        }

    except asyncio.TimeoutError:

        print(
            f"[GitVia] TIMEOUT → "
            f"{full_name}"
        )

        return None

    except GitHubAPIError as exc:

        print(
            f"[GitVia] GITHUB ERROR → "
            f"{full_name}: {exc}"
        )

        return None

    except Exception as exc:

        print(
            f"[GitVia] ERROR → "
            f"{full_name}: "
            f"{type(exc).__name__}: {exc}"
        )

        return None


# ============================================================
# ANALYZE ALL REPOSITORIES
# ============================================================

async def analyze_repositories(
    client: GitHubClient,
    github_repos: list[dict],
):

    analyzer = RepositoryAnalyzer()

    successful = []

    total = len(github_repos)

    print(
        "=================================================="
    )

    print(
        f"[GitVia] ANALYZING {total} REPOSITORIES"
    )

    print(
        "=================================================="
    )

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # Do NOT launch all repositories simultaneously.
    #
    # GitHub API calls are network-bound and launching 13+
    # repositories at once can cause connection timeouts.
    #
    # We intentionally process them sequentially here.
    # --------------------------------------------------------

    for index, repo in enumerate(
        github_repos,
        start=1,
    ):

        print(
            f"[GitVia] "
            f"Repository {index}/{total}"
        )

        result = await analyze_single_repository(
            client,
            analyzer,
            repo,
        )

        if result is not None:
            successful.append(result)

        print(
            f"[GitVia] "
            f"Progress: {index}/{total}"
        )

    print(
        "=================================================="
    )

    print(
        f"[GitVia] ANALYSIS COMPLETE → "
        f"{len(successful)}/{total} successful"
    )

    print(
        "=================================================="
    )

    return successful


# ============================================================
# SAVE ANALYSIS
# ============================================================

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

    existing.description = repo.get(
        "description"
    )

    existing.language = repo.get(
        "language"
    )

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

    existing.readme_content = item[
        "readme"
    ]

    existing.file_tree_json = item[
        "paths"
    ]

    db.flush()

    metric = (
        db.query(RepositoryMetric)
        .filter(
            RepositoryMetric.repo_id
            == existing.id
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

    metric.documentation_score = (
        analysis
        .get("documentation", {})
        .get("score", 0)
    )

    metric.architecture_score = (
        analysis
        .get("architecture", {})
        .get("score", 0)
    )

    metric.code_quality_score = (
        analysis
        .get("code_quality", {})
        .get("score", 0)
    )

    metric.testing_score = (
        analysis
        .get("testing", {})
        .get("score", 0)
    )

    metric.devops_score = (
        analysis
        .get("devops", {})
        .get("score", 0)
    )

    metric.scalability_score = (
        analysis
        .get("scalability", {})
        .get("score", 0)
    )

    metric.analysis_json = analysis

    metric.analyzed_at = datetime.utcnow()

    return existing


# ============================================================
# GET ALL REPOSITORIES
# ============================================================

@router.get("")
async def list_repositories(

    refresh: bool = Query(
        False,
        description=(
            "Force a fresh GitHub analysis"
        ),
    ),

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db),
):

    print(
        "[GitVia] GET /api/repos"
    )

    # --------------------------------------------------------
    # Authentication
    # --------------------------------------------------------

    if not current_user.access_token:

        raise HTTPException(
            status_code=401,
            detail=(
                "GitHub account is not connected"
            ),
        )

    # --------------------------------------------------------
    # CACHE
    # --------------------------------------------------------

    cached_repositories = (
        db.query(Repository)
        .filter(
            Repository.user_id
            == current_user.id
        )
        .all()
    )

    print(
        f"[GitVia] Cached repositories: "
        f"{len(cached_repositories)}"
    )

    # --------------------------------------------------------
    # Return cached data unless refresh was requested.
    # --------------------------------------------------------

    if cached_repositories and not refresh:

        print(
            "[GitVia] Returning cached repository data."
        )

        return [
            serialize_repository(repo)
            for repo in cached_repositories
        ]

    # --------------------------------------------------------
    # FRESH GITHUB ANALYSIS
    # --------------------------------------------------------

    print(
        "[GitVia] Starting fresh GitHub analysis..."
    )

    client = GitHubClient(
        current_user.access_token
    )

    try:

        github_repos = (
            await asyncio.wait_for(
                client.get_user_repos(),
                timeout=60,
            )
        )

    except asyncio.TimeoutError:

        raise HTTPException(
            status_code=504,
            detail=(
                "GitHub repository request timed out."
            ),
        )

    except GitHubAPIError as exc:

        print(
            f"[GitVia] GitHub error: {exc}"
        )

        raise HTTPException(
            status_code=502,
            detail=str(exc),
        )

    print(
        f"[GitVia] GitHub returned "
        f"{len(github_repos)} repositories."
    )

    # --------------------------------------------------------
    # Analyze repositories
    # --------------------------------------------------------

    analyzed = await analyze_repositories(
        client,
        github_repos,
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Commit once
    # --------------------------------------------------------

    db.commit()

    print(
        f"[GitVia] DATABASE SAVE COMPLETE → "
        f"{len(results)} repositories"
    )

    # --------------------------------------------------------
    # Serialize response
    # --------------------------------------------------------

    response = [
        serialize_repository(repo)
        for repo in results
    ]

    print(
        f"[GitVia] RESPONSE READY → "
        f"{len(response)} repositories"
    )

    return response


# ============================================================
# GET SINGLE REPOSITORY
# ============================================================

@router.get("/{repo_id}")
async def get_repository(

    repo_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db),
):

    repository = (
        db.query(Repository)
        .filter(
            Repository.user_id
            == current_user.id,

            Repository.github_repo_id
            == repo_id,
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