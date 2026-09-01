from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import DeveloperProfile, User, Repository, RepositoryMetric
from app.analyzers.profile_analyzer import ProfileAnalyzer
from app.github.client import GitHubClient

router = APIRouter(prefix="/api/profile", tags=["Developer Profile"])


@router.get("")
def get_developer_profile(db: Session = Depends(get_db)):
    profile = db.query(DeveloperProfile).first()
    if not profile:
        # Seed default profile dynamically
        client = GitHubClient()
        repos = client._get_mock_repos()
        from app.analyzers.repo_analyzer import RepositoryAnalyzer
        repo_analyzer = RepositoryAnalyzer()
        analyses = [repo_analyzer.analyze_repo(r["name"], r.get("readme_sample"), r.get("paths", []), r.get("language")) for r in repos]
        
        prof_analyzer = ProfileAnalyzer()
        res = prof_analyzer.analyze_profile(repos, analyses)

        return res

    return {
        "primary_role": profile.primary_role,
        "secondary_role": profile.secondary_role,
        "current_level": profile.current_level,
        "portfolio_score": profile.portfolio_score,
        "github_score": profile.github_score,
        "readiness_score": profile.readiness_score,
        "dimension_averages": {
            "projects": profile.portfolio_score,
            "github": profile.github_score,
            "documentation": 75.0,
            "testing": 62.0,
            "devops": 55.0,
            "scalability": 78.0,
        },
        "skill_scores": profile.skill_scores or {
            "Python": 90, "SQL": 81, "FastAPI": 85, "JavaScript": 72, "React": 63, "Docker": 42, "AWS": 31, "System Design": 70
        },
        "strongest_skills": profile.strongest_skills or ["APIs", "Python", "SQL"],
        "weakest_skills": profile.weakest_skills or ["Cloud", "Testing", "DevOps"],
        "top_recommendations": [
            "Add automated tests (Pytest/Jest) to project-x.",
            "Improve README architecture section with diagram.",
            "Add Dockerfile and docker-compose.yml.",
            "Add GitHub Actions automated workflow.",
            "Pin 3 strongest repositories with live demo link."
        ]
    }
