from typing import Any


class RoadmapGenerator:
    def generate_roadmap(
        self,
        dev_profile: dict[str, Any],
        user_repos: list[dict[str, Any]],
        target_role: str = "Python Backend Engineer"
    ) -> dict[str, Any]:
        """
        Generates a personalized, week-by-week actionable roadmap anchored directly to the user's existing projects.
        """
        repo_name = user_repos[0].get("name", "gitvia-career-copilot") if user_repos else "existing backend project"

        weekly_plan = [
            {
                "week": 1,
                "title": "Docker Containerization Fundamentals",
                "focus": "DevOps & Infrastructure",
                "status": "In Progress",
                "deliverable": f"Write a multi-stage Dockerfile for '{repo_name}' and test local container execution.",
                "guidance": f"💡 Recommendation: Don't build another Todo app. Write a production Dockerfile for your existing repository '{repo_name}' to containerize your FastAPI/Python service.",
                "tasks": [
                    f"Create `Dockerfile` in `{repo_name}` root with Python 3.11-slim base image.",
                    "Optimize layer caching for `requirements.txt` dependencies.",
                    "Run container locally with environment variable bindings (`docker run -p 8000:8000`)."
                ]
            },
            {
                "week": 2,
                "title": "Docker Compose & Local Multi-Container Services",
                "focus": "Database & Orchestration",
                "status": "Upcoming",
                "deliverable": f"Add `docker-compose.yml` orchestrating `{repo_name}` alongside PostgreSQL and Redis.",
                "guidance": f"💡 Action: Wire up your database and background worker containers in `{repo_name}` so your whole stack boots with a single `docker compose up` command.",
                "tasks": [
                    "Define `postgres:17` container service with persistent volumes.",
                    "Define `redis:7-alpine` cache service.",
                    "Configure healthchecks and service dependency order (`depends_on`)."
                ]
            },
            {
                "week": 3,
                "title": "Automated CI/CD with GitHub Actions",
                "focus": "Automation & Quality Assurance",
                "status": "Upcoming",
                "deliverable": f"Set up `.github/workflows/ci.yml` in `{repo_name}` to automatically run Pytest and lint checks on every PR.",
                "guidance": "💡 Action: Ensure every future pull request is automatically tested before merge.",
                "tasks": [
                    "Create workflow triggering on `push` and `pull_request` to `main` branch.",
                    "Add step to install dependencies and run `pytest` test suite.",
                    "Add Docker image build verification step."
                ]
            },
            {
                "week": 4,
                "title": "Cloud Deployment (AWS / Render / Railway)",
                "focus": "Cloud Architecture",
                "status": "Upcoming",
                "deliverable": f"Deploy `{repo_name}` to AWS ECS/AppRunner or Render and attach live URL to README.",
                "guidance": "💡 Action: Turn your GitHub code into a live production service accessible to hiring managers.",
                "tasks": [
                    "Provision cloud PostgreSQL instance.",
                    "Configure production environment secrets.",
                    "Deploy container image and update repository README with live API badge."
                ]
            },
            {
                "week": 5,
                "title": "Asynchronous Background Jobs & Caching with Redis",
                "focus": "Scalability & Performance",
                "status": "Upcoming",
                "deliverable": f"Integrate Redis & Celery into `{repo_name}` to offload heavy analysis jobs.",
                "guidance": "💡 Action: Upgrade HTTP response latency by moving long-running tasks into asynchronous queues.",
                "tasks": [
                    "Configure Celery app worker instance.",
                    "Cache frequent GET API responses in Redis with 10-minute TTL.",
                    "Measure and document API response speedup in README benchmark section."
                ]
            },
            {
                "week": 6,
                "title": "System Architecture & High-Availability Design",
                "focus": "System Design",
                "status": "Upcoming",
                "deliverable": "Create a C4 System Architecture diagram and prepare for senior technical interviews.",
                "guidance": "💡 Action: Document your data flows and component boundaries to ace system design interviews.",
                "tasks": [
                    "Draw Mermaid.js sequence and component diagrams for GitVia architecture.",
                    "Document database indexing strategy and query execution plans.",
                    "Complete mock interview practice for system design trade-offs."
                ]
            }
        ]

        return {
            "target_role": target_role,
            "duration_weeks": 6,
            "headline": f"Personalized 6-Week Action Plan for {target_role}",
            "weekly_plan": weekly_plan
        }
