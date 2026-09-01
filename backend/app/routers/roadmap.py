from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.analyzers.roadmap_generator import RoadmapGenerator
from app.analyzers.profile_analyzer import ProfileAnalyzer
from app.github.client import GitHubClient

router = APIRouter(prefix="/api/roadmap", tags=["Personalized Learning Roadmap"])


@router.get("")
def get_roadmap(target_role: str = "Backend Engineer", db: Session = Depends(get_db)):
    client = GitHubClient()
    repos = client._get_mock_repos()

    from app.analyzers.repo_analyzer import RepositoryAnalyzer
    repo_analyzer = RepositoryAnalyzer()
    analyses = [repo_analyzer.analyze_repo(r["name"], r.get("readme_sample"), r.get("paths", []), r.get("language")) for r in repos]

    prof_analyzer = ProfileAnalyzer()
    dev_profile = prof_analyzer.analyze_profile(repos, analyses)

    generator = RoadmapGenerator()
    roadmap = generator.generate_roadmap(dev_profile, repos, target_role)

    return roadmap
