from fastapi import APIRouter, Depends, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.analyzers.resume_analyzer import ResumeAnalyzer
from app.analyzers.job_analyzer import JobAnalyzer
from app.analyzers.profile_analyzer import ProfileAnalyzer
from app.github.client import GitHubClient

router = APIRouter(prefix="/api/career", tags=["Career Intelligence & Matching"])


class JobAnalyzeRequest(BaseModel):
    title: str = "Amazon SDE Intern"
    company: str = "Amazon"
    job_text: str


@router.post("/resume/upload")
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    analyzer = ResumeAnalyzer()
    raw_text = analyzer.extract_text_from_pdf(contents)

    client = GitHubClient()
    mock_repos = client._get_mock_repos()

    analysis = analyzer.analyze_resume(raw_text, mock_repos)

    return {
        "filename": file.filename,
        "raw_text_length": len(raw_text),
        "parsed_skills": analysis["parsed_skills"],
        "education": analysis["education"],
        "experience": analysis["experience"],
        "mismatch_flags": analysis["mismatch_flags"],
        "bullets_suggestions": analysis["bullets_suggestions"]
    }


@router.post("/jobs/analyze")
def analyze_job_description(req: JobAnalyzeRequest, db: Session = Depends(get_db)):
    client = GitHubClient()
    repos = client._get_mock_repos()

    from app.analyzers.repo_analyzer import RepositoryAnalyzer
    repo_analyzer = RepositoryAnalyzer()
    analyses = [repo_analyzer.analyze_repo(r["name"], r.get("readme_sample"), r.get("paths", []), r.get("language")) for r in repos]
    
    prof_analyzer = ProfileAnalyzer()
    dev_profile = prof_analyzer.analyze_profile(repos, analyses)

    job_analyzer = JobAnalyzer()
    result = job_analyzer.analyze_job(req.title, req.company, req.job_text, dev_profile)

    return result
