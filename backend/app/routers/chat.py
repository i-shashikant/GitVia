from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.analyzers.career_chat import CareerChatAssistant
from app.analyzers.profile_analyzer import ProfileAnalyzer
from app.github.client import GitHubClient

router = APIRouter(prefix="/api/chat", tags=["AI Career Assistant Chat"])


class ChatRequest(BaseModel):
    message: str


@router.post("")
def chat_with_assistant(req: ChatRequest, db: Session = Depends(get_db)):
    client = GitHubClient()
    repos = client._get_mock_repos()

    from app.analyzers.repo_analyzer import RepositoryAnalyzer
    repo_analyzer = RepositoryAnalyzer()
    analyses = [repo_analyzer.analyze_repo(r["name"], r.get("readme_sample"), r.get("paths", []), r.get("language")) for r in repos]

    prof_analyzer = ProfileAnalyzer()
    dev_profile = prof_analyzer.analyze_profile(repos, analyses)

    assistant = CareerChatAssistant()
    reply = assistant.generate_response(req.message, dev_profile, repos)

    return {
        "query": req.message,
        "response": reply
    }
