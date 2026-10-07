from app.analyzers.repo_analyzer import RepositoryAnalyzer
from app.analyzers.profile_analyzer import ProfileAnalyzer
from app.analyzers.resume_analyzer import ResumeAnalyzer
from app.analyzers.job_analyzer import JobAnalyzer
from app.analyzers.roadmap_generator import RoadmapGenerator
from app.analyzers.career_chat import CareerChatAssistant
from app.security.crypto import decrypt_token, encrypt_token


SAMPLE_REPOS = [
    {
        "name": "backend-api",
        "language": "Python",
        "description": "FastAPI REST API with PostgreSQL",
        "readme_sample": "# Backend API\n## Architecture\nModular FastAPI app.\n## Usage\nRun pytest.",
        "paths": [
            "app/main.py",
            "app/models.py",
            "tests/test_main.py",
            "Dockerfile",
            ".github/workflows/ci.yml",
        ],
    }
]


def _analyses():
    analyzer = RepositoryAnalyzer()
    return [
        analyzer.analyze_repo(
            repo["name"],
            repo["readme_sample"],
            repo["paths"],
            repo["language"],
        )
        for repo in SAMPLE_REPOS
    ]


def test_repo_analyzer():
    analyzer = RepositoryAnalyzer()
    res = analyzer.analyze_repo(
        name="test-repo",
        readme="# Test Repo\n## Architecture\nClean modular layout.\n## Usage\nRun pytest.",
        paths=[
            "app/main.py",
            "app/models.py",
            "tests/test_main.py",
            "Dockerfile",
            ".github/workflows/ci.yml",
        ],
        language="Python",
    )
    assert res["overall_score"] > 60
    assert res["testing"]["score"] == 45
    assert res["devops"]["score"] == 95
    assert res["name"] == "test-repo"
    assert "Docker" in res["tech_stack"]


def test_profile_analyzer():
    analyses = _analyses()
    profile = ProfileAnalyzer().analyze_profile(SAMPLE_REPOS, analyses)
    assert profile["portfolio_score"] > 60
    assert "Python" in profile["skill_scores"]
    assert profile["primary_role"]


def test_empty_profile_is_zero():
    profile = ProfileAnalyzer().analyze_profile([], [])
    assert profile["portfolio_score"] == 0
    assert profile["skill_scores"] == {}


def test_resume_mismatch_detection():
    analyzer = ResumeAnalyzer()
    repos = [
        {
            "name": "backend-api",
            "language": "Python",
            "tech_stack": ["Python", "FastAPI"],
        }
    ]
    resume_text = "Experienced developer with Kubernetes and AWS background."
    res = analyzer.analyze_resume(resume_text, repos)
    assert len(res["mismatch_flags"]) > 0
    assert any(
        "Kubernetes" in m["skill"] or "AWS" in m["skill"]
        for m in res["mismatch_flags"]
    )


def test_job_analyzer():
    analyzer = JobAnalyzer()
    dev_profile = {
        "skill_scores": {"Python": 90, "FastAPI": 85, "SQL": 80},
        "dimension_averages": {"devops": 45, "projects": 80, "code_quality": 70},
    }
    res = analyzer.analyze_job(
        "Backend Intern",
        "Amazon",
        "Looking for Python, FastAPI, Docker, AWS, Kubernetes expertise.",
        dev_profile,
    )
    assert res["match_score"] > 40
    assert "Python" in res["skill_gaps"]["strong"]
    assert (
        "Kubernetes" in res["skill_gaps"]["missing"]
        or "Docker" in res["skill_gaps"]["missing"]
        or "Docker" in res["skill_gaps"]["improving"]
    )


def test_job_analyzer_detects_common_languages_and_primary_repo_language():
    analyzer = JobAnalyzer()

    res = analyzer.analyze_job(
        "Software Development",
        "Acme",
        "Required: .NET, C++ Programming, Java, Python, JavaScript, Kubernetes.",
        {"skill_scores": {"Python": 85}},
        [{"name": "cpp-service", "language": "C++", "tech_stack": []}],
    )

    assert ".NET" in res["required_skills"]
    assert "C++" in res["required_skills"]
    assert "Java" in res["required_skills"]
    assert "Kubernetes" in res["required_skills"]

    cpp_result = next(
        item for item in res["skill_results"] if item["skill"] == "C++"
    )
    assert cpp_result["developer_score"] >= 45

def test_roadmap_generator():
    generator = RoadmapGenerator()
    dev_profile = {}
    repos = [{"name": "my-backend-repo"}]
    roadmap = generator.generate_roadmap(dev_profile, repos, "Backend Engineer")
    assert len(roadmap["weekly_plan"]) == 6
    assert roadmap["weekly_plan"][0]["title"]




def test_job_specific_roadmap_uses_job_requirements():
    generator = RoadmapGenerator()

    dev_profile = {
        "strongest_skills": ["Python", "JavaScript", "React"],
        "weakest_skills": ["Testing"],
        "skill_scores": {
            "Python": 90,
            "JavaScript": 85,
            "React": 80,
            "Testing": 55,
        },
        "job_required_skills": [
            ".NET",
            "C++",
            "Java",
            "JavaScript",
            "Python",
            "React",
            "MySQL",
            "Node.js",
            "Testing",
        ],
        "job_preferred_skills": [],
        "job_missing_skills": [
            ".NET",
            "C++",
            "Java",
            "MySQL",
            "Node.js",
        ],
    }

    roadmap = generator.generate_roadmap(
        dev_profile,
        [{"name": "gitvia"}],
        "Software Development",
    )

    assert roadmap["job_specific"] is True
    assert roadmap["target_role"] == "Software Development"
    assert ".NET" in roadmap["missing_skills"]
    assert "C++" in roadmap["missing_skills"]
    assert "Java" in roadmap["missing_skills"]
    assert "Python" in roadmap["strong_skills"]
    assert roadmap["weekly_plan"][0]["tasks"][0]["skills"][0] in {
        ".NET",
        "C++",
        "Java",
        "MySQL",
        "Node.js",
    }


def test_career_chat():
    assistant = CareerChatAssistant()
    dev_profile = {
        "portfolio_score": 81,
        "readiness_score": 76,
        "strongest_skills": ["Python", "SQL"],
        "weakest_skills": ["DevOps"],
    }
    repos = [{"name": "my-backend-repo"}]

    ans = assistant.generate_response(
        "Am I ready for backend internships?",
        dev_profile,
        repos,
    )
    assert "Readiness score" in ans or "ready" in ans.lower() or "Python" in ans


def test_token_roundtrip():
    token = "gho_test_access_token"
    stored = encrypt_token(token)
    assert stored != token
    assert decrypt_token(stored) == token
    assert decrypt_token(token) == token
