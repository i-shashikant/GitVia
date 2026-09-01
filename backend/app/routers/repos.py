from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.github.client import GitHubClient
from app.analyzers.repo_analyzer import RepositoryAnalyzer

router = APIRouter(prefix="/api/repos", tags=["Repositories & Code Quality"])


@router.get("")
def list_repositories(db: Session = Depends(get_db)):
    client = GitHubClient()
    repos = client._get_mock_repos()
    analyzer = RepositoryAnalyzer()

    results = []
    for r in repos:
        analysis = analyzer.analyze_repo(
            name=r["name"],
            readme=r.get("readme_sample"),
            paths=r.get("paths", []),
            language=r.get("language"),
            stars=r.get("stargazers_count", 0),
            forks=r.get("forks_count", 0)
        )
        results.append({
            "id": r["id"],
            "name": r["name"],
            "full_name": r["full_name"],
            "description": r["description"],
            "language": r["language"],
            "stars_count": r["stargazers_count"],
            "forks_count": r["forks_count"],
            "html_url": r["html_url"],
            "tech_stack": r.get("tech_stack", []),
            "quality_score": analysis["overall_score"],
            "analysis": analysis
        })

    return results


@router.get("/{repo_id}")
def get_repository_detail(repo_id: int, db: Session = Depends(get_db)):
    client = GitHubClient()
    repos = client._get_mock_repos()
    repo = next((r for r in repos if r["id"] == repo_id), None)
    if not repo:
        repo = repos[0]

    analyzer = RepositoryAnalyzer()
    analysis = analyzer.analyze_repo(
        name=repo["name"],
        readme=repo.get("readme_sample"),
        paths=repo.get("paths", []),
        language=repo.get("language"),
        stars=repo.get("stargazers_count", 0),
        forks=repo.get("forks_count", 0)
    )

    return {
        "id": repo["id"],
        "name": repo["name"],
        "full_name": repo["full_name"],
        "description": repo["description"],
        "language": repo["language"],
        "stars_count": repo["stargazers_count"],
        "forks_count": repo["forks_count"],
        "html_url": repo["html_url"],
        "readme": repo.get("readme_sample"),
        "tech_stack": repo.get("tech_stack", []),
        "paths": repo.get("paths", []),
        "quality_score": analysis["overall_score"],
        "analysis": analysis
    }
