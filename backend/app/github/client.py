import os
from typing import Any
import httpx


class GitHubClient:
    def __init__(self, access_token: str | None = None):
        self.access_token = access_token
        self.headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "GitVia-Career-Intelligence",
        }
        if access_token:
            self.headers["Authorization"] = f"Bearer {access_token}"

    async def get_user_profile(self, username: str | None = None) -> dict[str, Any]:
        url = f"https://api.github.com/users/{username}" if username else "https://api.github.com/user"
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=self.headers)
            if res.status_code == 200:
                return res.json()
        return self._get_mock_profile(username or "shashikant")

    async def get_user_repos(self, username: str | None = None) -> list[dict[str, Any]]:
        url = f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated" if username else "https://api.github.com/user/repos?per_page=100&sort=updated"
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=self.headers)
            if res.status_code == 200:
                return res.json()
        return self._get_mock_repos()

    async def get_repo_details(self, owner: str, repo: str) -> dict[str, Any]:
        url = f"https://api.github.com/repos/{owner}/{repo}"
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=self.headers)
            if res.status_code == 200:
                return res.json()
        return {}

    async def get_repo_readme(self, owner: str, repo: str) -> str | None:
        url = f"https://api.github.com/repos/{owner}/{repo}/readme"
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers={"Accept": "application/vnd.github.raw+json", **self.headers})
            if res.status_code == 200:
                return res.text
        return None

    async def get_repo_tree(self, owner: str, repo: str, branch: str = "main") -> list[str]:
        url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=self.headers)
            if res.status_code == 200:
                data = res.json()
                return [item["path"] for item in data.get("tree", []) if item["type"] == "blob"]
        return []

    def _get_mock_profile(self, username: str) -> dict[str, Any]:
        return {
            "login": username,
            "id": 98765432,
            "name": "Shashikant Kumar",
            "bio": "Full Stack & AI Engineer | Building Scalable Systems",
            "public_repos": 14,
            "followers": 128,
            "following": 45,
            "avatar_url": "https://avatars.githubusercontent.com/u/98765432?v=4",
        }

    def _get_mock_repos(self) -> list[dict[str, Any]]:
        return [
            {
                "id": 101,
                "name": "gitvia-career-copilot",
                "full_name": "shashikant/gitvia-career-copilot",
                "description": "AI career intelligence platform analyzing GitHub repos, resumes, and job specs.",
                "language": "Python",
                "stargazers_count": 42,
                "forks_count": 12,
                "fork": False,
                "default_branch": "main",
                "html_url": "https://github.com/shashikant/gitvia-career-copilot",
                "readme_sample": """# GitVia AI Copilot\nAn AI career intelligence platform with FastAPI, Next.js, and PostgreSQL.\n## Architecture\nUses hybrid deterministic code analysis + LLM reasoning.\n## Features\n- GitHub Analyzer\n- Repository Quality Score\n- Skill Gap Matrix\n""",
                "paths": [
                    "backend/app/main.py",
                    "backend/app/models.py",
                    "backend/app/analyzers/repo_analyzer.py",
                    "backend/requirements.txt",
                    "docker-compose.yml",
                    "frontend/src/app/page.tsx",
                    "README.md"
                ],
                "tech_stack": ["Python", "FastAPI", "Next.js", "TypeScript", "PostgreSQL", "Docker"]
            },
            {
                "id": 102,
                "name": "distributed-task-engine",
                "full_name": "shashikant/distributed-task-engine",
                "description": "High-throughput asynchronous task engine using Redis, Python async, and worker pools.",
                "language": "Python",
                "stargazers_count": 28,
                "forks_count": 5,
                "fork": False,
                "default_branch": "main",
                "html_url": "https://github.com/shashikant/distributed-task-engine",
                "readme_sample": """# Distributed Task Engine\nAsynchronous queue worker engine built with Redis and PyTest.\n## Tests\nRun `pytest tests/` for full coverage.\n""",
                "paths": [
                    "engine/worker.py",
                    "engine/queue.py",
                    "tests/test_worker.py",
                    "Dockerfile",
                    ".github/workflows/ci.yml",
                    "requirements.txt",
                    "README.md"
                ],
                "tech_stack": ["Python", "Redis", "Docker", "Pytest", "CI/CD"]
            },
            {
                "id": 103,
                "name": "react-analytics-dashboard",
                "full_name": "shashikant/react-analytics-dashboard",
                "description": "Real-time user telemetry and chart dashboard powered by React and Tailwind CSS.",
                "language": "TypeScript",
                "stargazers_count": 19,
                "forks_count": 3,
                "fork": False,
                "default_branch": "main",
                "html_url": "https://github.com/shashikant/react-analytics-dashboard",
                "readme_sample": """# React Analytics Dashboard\nVisual metrics dashboard using Recharts and Tailwind.\n""",
                "paths": [
                    "src/components/Chart.tsx",
                    "src/pages/Dashboard.tsx",
                    "package.json",
                    "README.md"
                ],
                "tech_stack": ["TypeScript", "React", "Tailwind CSS", "Recharts"]
            },
            {
                "id": 104,
                "name": "microservices-api-gateway",
                "full_name": "shashikant/microservices-api-gateway",
                "description": "REST API gateway routing, rate limiting, and JWT authentication service.",
                "language": "Go",
                "stargazers_count": 15,
                "forks_count": 2,
                "fork": False,
                "default_branch": "main",
                "html_url": "https://github.com/shashikant/microservices-api-gateway",
                "readme_sample": """# API Gateway\nAPI routing gateway in Go.\n""",
                "paths": [
                    "main.go",
                    "router/gateway.go",
                    "docker-compose.yml",
                    "README.md"
                ],
                "tech_stack": ["Go", "Docker", "JWT", "REST API"]
            }
        ]
