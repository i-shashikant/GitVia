from typing import Any


class RepositoryAnalyzer:
    def analyze_repo(
        self,
        name: str,
        readme: str | None,
        paths: list[str],
        language: str | None,
        stars: int = 0,
        forks: int = 0
    ) -> dict[str, Any]:
        """
        Calculates deterministic and AI-enhanced quality metrics across 6 dimensions:
        1. Documentation
        2. Architecture
        3. Code Quality
        4. Testing
        5. DevOps
        6. Scalability
        """
        paths_set = set(p.lower() for p in paths)
        readme_lower = (readme or "").lower()

        # 1. Documentation Score (0-100)
        doc_score = 40
        doc_reasons = []
        if readme:
            doc_score += 25
            if len(readme) > 500:
                doc_score += 15
            if "architecture" in readme_lower or "design" in readme_lower:
                doc_score += 10
                doc_reasons.append("README includes architecture/design breakdown.")
            else:
                doc_reasons.append("README lacks an explicit Architecture section.")
            if "installation" in readme_lower or "usage" in readme_lower or "getting started" in readme_lower:
                doc_score += 10
                doc_reasons.append("Includes setup and getting started guide.")
        else:
            doc_reasons.append("Missing README.md file.")

        doc_score = min(100, max(10, doc_score))

        # 2. Architecture Score (0-100)
        arch_score = 50
        arch_reasons = []
        has_layers = any(
            any(folder in p for folder in ["app/", "src/", "controllers/", "services/", "models/", "routes/", "components/", "backend/", "frontend/"])
            for p in paths_set
        )
        if has_layers:
            arch_score += 30
            arch_reasons.append("Clean separation of concerns into modular directory layers.")
        else:
            arch_reasons.append("Flat file structure with limited component modularization.")

        if any("config" in p or "env" in p or "settings" in p for p in paths_set):
            arch_score += 15
            arch_reasons.append("Centralized configuration management detected.")

        arch_score = min(100, max(20, arch_score))

        # 3. Code Quality Score (0-100)
        code_score = 60
        code_reasons = []
        if len(paths) > 5:
            code_score += 15
            code_reasons.append("Structured codebase with multiple modular files.")
        if any(p.endswith((".py", ".ts", ".tsx", ".go", ".rs", ".java")) for p in paths_set):
            code_score += 15
            code_reasons.append("Written in a modern strongly-typed or structured language.")

        code_score = min(100, max(30, code_score))

        # 4. Testing Score (0-100)
        test_score = 15
        test_reasons = []
        has_tests = any(
            "test" in p or "spec" in p or p.startswith("tests/")
            for p in paths_set
        )
        if has_tests:
            test_score = 85
            test_reasons.append("Automated test suite identified in project files.")
        else:
            test_score = 30
            test_reasons.append("No automated test suite (pytest/jest/unit tests) detected.")

        # 5. DevOps Score (0-100)
        devops_score = 15
        devops_reasons = []
        has_docker = any("dockerfile" in p or "docker-compose" in p for p in paths_set)
        has_ci = any(".github/workflows" in p or "ci" in p or "pipeline" in p for p in paths_set)

        if has_docker:
            devops_score += 40
            devops_reasons.append("Containerization enabled via Dockerfile / Docker Compose.")
        else:
            devops_reasons.append("Missing Docker containerization configuration.")

        if has_ci:
            devops_score += 40
            devops_reasons.append("Automated CI/CD workflows detected (GitHub Actions).")
        else:
            devops_reasons.append("Missing automated CI/CD deployment pipeline.")

        devops_score = min(100, max(15, devops_score))

        # 6. Scalability Score (0-100)
        scale_score = 55
        scale_reasons = []
        if any(db in readme_lower or any(db in p for p in paths_set) for db in ["postgres", "redis", "mongodb", "kafka", "queue", "celery"]):
            scale_score += 30
            scale_reasons.append("Integrates production database / asynchronous cache or queue.")
        else:
            scale_reasons.append("No asynchronous task processing or caching layer identified.")

        scale_score = min(100, max(35, scale_score))

        # Weighted Overall Project Quality Score
        overall_score = round(
            (doc_score * 0.20) +
            (arch_score * 0.20) +
            (code_score * 0.20) +
            (test_score * 0.15) +
            (devops_score * 0.15) +
            (scale_score * 0.10),
            1
        )

        # Generate Actionable Improvements
        improvements = []
        if test_score < 70:
            improvements.append(f"Add automated tests (e.g. Pytest or Jest) to {name}.")
        if devops_score < 60:
            if not has_docker:
                improvements.append(f"Add a Dockerfile and docker-compose.yml to containerize {name}.")
            if not has_ci:
                improvements.append(f"Configure a GitHub Actions workflow (.github/workflows/ci.yml) for automated builds and testing.")
        if doc_score < 75:
            improvements.append("Expand README.md with an explicit System Architecture diagram and step-by-step setup guide.")
        if scale_score < 70:
            improvements.append("Introduce Redis caching or asynchronous Celery background workers for background processing.")

        return {
            "overall_score": overall_score,
            "documentation": {"score": doc_score, "reasons": doc_reasons},
            "architecture": {"score": arch_score, "reasons": arch_reasons},
            "code_quality": {"score": code_score, "reasons": code_reasons},
            "testing": {"score": test_score, "reasons": test_reasons},
            "devops": {"score": devops_score, "reasons": devops_reasons},
            "scalability": {"score": scale_score, "reasons": scale_reasons},
            "actionable_improvements": improvements
        }
