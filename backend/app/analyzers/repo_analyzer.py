import logging
from typing import Any

logger = logging.getLogger(__name__)


TECH_HINTS = {
    "docker": "Docker",
    "dockerfile": "Docker",
    "docker-compose": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "terraform": "Terraform",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "react": "React",
    "next": "Next.js",
    "pytest": "Pytest",
    "redis": "Redis",
    "postgres": "PostgreSQL",
    "celery": "Celery",
    "aws": "AWS",
}


class RepositoryAnalyzer:

    def analyze_repo(
        self,
        name: str,
        readme: str | None,
        paths: list[str],
        language: str | None,
        stars: int = 0,
        forks: int = 0,
    ) -> dict[str, Any]:
        """
        Analyze a GitHub repository across six engineering dimensions:

        1. Documentation
        2. Architecture
        3. Code Quality
        4. Testing
        5. DevOps
        6. Scalability

        Returns deterministic scores and actionable recommendations.
        """

        logger.debug(
            "Analyzing %s readme=%s paths=%s language=%s stars=%s forks=%s",
            name,
            bool(readme),
            len(paths),
            language,
            stars,
            forks,
        )

        # ============================================================
        # NORMALIZE INPUT
        # ============================================================

        paths_set = set(p.lower() for p in paths)

        readme_lower = (readme or "").lower()

        # ============================================================
        # 1. DOCUMENTATION SCORE
        # ============================================================

        doc_score = 40
        doc_reasons = []

        if readme:

            doc_score += 25

            if len(readme) > 500:
                doc_score += 15

            if (
                "architecture" in readme_lower
                or "design" in readme_lower
            ):
                doc_score += 10

                doc_reasons.append(
                    "README includes architecture/design breakdown."
                )

            else:

                doc_reasons.append(
                    "README lacks an explicit Architecture section."
                )

            if (
                "installation" in readme_lower
                or "usage" in readme_lower
                or "getting started" in readme_lower
            ):
                doc_score += 10

                doc_reasons.append(
                    "Includes setup and getting started guide."
                )

        else:

            doc_reasons.append(
                "Missing README.md file."
            )

        doc_score = min(
            100,
            max(10, doc_score)
        )

        # ============================================================
        # 2. ARCHITECTURE SCORE
        # ============================================================

        arch_score = 50
        arch_reasons = []

        architecture_folders = [
            "app/",
            "src/",
            "controllers/",
            "services/",
            "models/",
            "routes/",
            "components/",
            "backend/",
            "frontend/",
        ]

        has_layers = any(
            any(
                folder in path
                for folder in architecture_folders
            )
            for path in paths_set
        )

        if has_layers:

            arch_score += 30

            arch_reasons.append(
                "Clean separation of concerns into modular directory layers."
            )

        else:

            arch_reasons.append(
                "Flat file structure with limited component modularization."
            )

        has_config = any(
            (
                "config" in path
                or "env" in path
                or "settings" in path
            )
            for path in paths_set
        )

        if has_config:

            arch_score += 15

            arch_reasons.append(
                "Centralized configuration management detected."
            )

        arch_score = min(
            100,
            max(20, arch_score)
        )

        # ============================================================
        # 3. CODE QUALITY SCORE
        # ============================================================

        code_score = 60
        code_reasons = []

        if len(paths) > 5:

            code_score += 15

            code_reasons.append(
                "Structured codebase with multiple modular files."
            )

        structured_extensions = (
            ".py",
            ".ts",
            ".tsx",
            ".go",
            ".rs",
            ".java",
        )

        has_structured_code = any(
            path.endswith(structured_extensions)
            for path in paths_set
        )

        if has_structured_code:

            code_score += 15

            code_reasons.append(
                "Written in a modern strongly-typed or structured language."
            )

        code_score = min(
            100,
            max(30, code_score)
        )

        # ============================================================
        # 4. TESTING SCORE
        # ============================================================

        test_score = 15
        test_reasons = []

        has_tests = any(
            (
                "test" in path
                or "spec" in path
                or path.startswith("tests/")
            )
            for path in paths_set
        )

        if has_tests:

            test_score = 85

            test_reasons.append(
                "Automated test suite identified in project files."
            )

        else:

            test_score = 30

            test_reasons.append(
                "No automated test suite (pytest/jest/unit tests) detected."
            )

        # ============================================================
        # 5. DEVOPS SCORE
        # ============================================================

        devops_score = 15
        devops_reasons = []

        has_docker = any(
            (
                "dockerfile" in path
                or "docker-compose" in path
            )
            for path in paths_set
        )

        has_ci = any(
            (
                ".github/workflows" in path
                or "ci" in path
                or "pipeline" in path
            )
            for path in paths_set
        )

        if has_docker:

            devops_score += 40

            devops_reasons.append(
                "Containerization enabled via Dockerfile / Docker Compose."
            )

        else:

            devops_reasons.append(
                "Missing Docker containerization configuration."
            )

        if has_ci:

            devops_score += 40

            devops_reasons.append(
                "Automated CI/CD workflows detected (GitHub Actions)."
            )

        else:

            devops_reasons.append(
                "Missing automated CI/CD deployment pipeline."
            )

        devops_score = min(
            100,
            max(15, devops_score)
        )

        # ============================================================
        # 6. SCALABILITY SCORE
        # ============================================================

        scale_score = 55
        scale_reasons = []

        scalability_keywords = [
            "postgres",
            "redis",
            "mongodb",
            "kafka",
            "queue",
            "celery",
        ]

        has_scalability_stack = any(
            (
                keyword in readme_lower
                or any(
                    keyword in path
                    for path in paths_set
                )
            )
            for keyword in scalability_keywords
        )

        if has_scalability_stack:

            scale_score += 30

            scale_reasons.append(
                "Integrates production database / asynchronous cache or queue."
            )

        else:

            scale_reasons.append(
                "No asynchronous task processing or caching layer identified."
            )

        scale_score = min(
            100,
            max(35, scale_score)
        )

        # ============================================================
        # WEIGHTED OVERALL SCORE
        # ============================================================

        overall_score = round(
            (doc_score * 0.20)
            + (arch_score * 0.20)
            + (code_score * 0.20)
            + (test_score * 0.15)
            + (devops_score * 0.15)
            + (scale_score * 0.10),
            1,
        )

        # ============================================================
        # ACTIONABLE IMPROVEMENTS
        # ============================================================

        improvements = []

        if test_score < 70:

            improvements.append(
                f"Add automated tests (e.g. Pytest or Jest) to {name}."
            )

        if devops_score < 60:

            if not has_docker:

                improvements.append(
                    f"Add a Dockerfile and docker-compose.yml "
                    f"to containerize {name}."
                )

            if not has_ci:

                improvements.append(
                    "Configure a GitHub Actions workflow "
                    "(.github/workflows/ci.yml) for automated builds and testing."
                )

        if doc_score < 75:

            improvements.append(
                "Expand README.md with an explicit System Architecture "
                "diagram and step-by-step setup guide."
            )

        if scale_score < 70:

            improvements.append(
                "Introduce Redis caching or asynchronous Celery "
                "background workers for background processing."
            )

        tech_stack = []
        haystack = " ".join(paths_set) + " " + readme_lower
        if language:
            tech_stack.append(language)
        for hint, label in TECH_HINTS.items():
            if hint in haystack and label not in tech_stack:
                tech_stack.append(label)

        logger.debug(
            "Scored %s overall=%s doc=%s arch=%s code=%s test=%s devops=%s scale=%s",
            name,
            overall_score,
            doc_score,
            arch_score,
            code_score,
            test_score,
            devops_score,
            scale_score,
        )

        return {
            "name": name,
            "overall_score": overall_score,
            "tech_stack": tech_stack,

            "documentation": {
                "score": doc_score,
                "reasons": doc_reasons,
            },

            "architecture": {
                "score": arch_score,
                "reasons": arch_reasons,
            },

            "code_quality": {
                "score": code_score,
                "reasons": code_reasons,
            },

            "testing": {
                "score": test_score,
                "reasons": test_reasons,
            },

            "devops": {
                "score": devops_score,
                "reasons": devops_reasons,
            },

            "scalability": {
                "score": scale_score,
                "reasons": scale_reasons,
            },

            "actionable_improvements": improvements,
        }