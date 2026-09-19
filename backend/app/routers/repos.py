from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.session import get_current_user
from app.database import get_db
from app.github.client import GitHubAPIError, GitHubClient
from app.models import User
from app.analyzers.repo_analyzer import RepositoryAnalyzer


router = APIRouter(
    prefix="/api/repos",
    tags=["Repositories & Code Quality"],
)


@router.get("")
async def list_repositories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.access_token:
        raise HTTPException(
            status_code=401,
            detail="GitHub account is not connected",
        )

    client = GitHubClient(
        current_user.access_token
    )

    analyzer = RepositoryAnalyzer()

    try:
        github_repos = await client.get_user_repos()

    except GitHubAPIError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        )

    results = []

    for repo in github_repos:

        owner = repo["owner"]["login"]
        name = repo["name"]
        branch = repo.get("default_branch") or "main"

        readme = await client.get_repo_readme(
            owner,
            name,
        )

        paths = await client.get_repo_tree(
            owner,
            name,
            branch,
        )

        analysis = analyzer.analyze_repo(
            name=name,
            readme=readme,
            paths=paths,
            language=repo.get("language"),
            stars=repo.get("stargazers_count", 0),
            forks=repo.get("forks_count", 0),
        )

        results.append(
            {
                "id": repo["id"],
                "name": name,
                "full_name": repo["full_name"],
                "description": repo.get("description"),
                "language": repo.get("language"),
                "stars_count": repo.get("stargazers_count", 0),
                "forks_count": repo.get("forks_count", 0),
                "html_url": repo["html_url"],
                "default_branch": branch,
                "is_fork": repo.get("fork", False),
                "quality_score": analysis["overall_score"],
                "analysis": analysis,
            }
        )

    return results