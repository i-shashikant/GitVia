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
        sampled_files: dict[str, str] | None = None,
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

        sampled_files = sampled_files or {}

        sampled_text = "\n".join(
            content.lower()
            for content in sampled_files.values()
        )

        sampled_paths = {
            path.lower()
            for path in sampled_files
        }

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

                # ============================================================
        # 4. TESTING SCORE
        # ============================================================

        test_score = 20
        test_reasons = []

        test_files = [
            path
            for path in paths_set
            if (
                path.startswith("tests/")
                or "/tests/" in path
                or "/test/" in path
                or path.startswith("test_")
                or path.endswith("_test.py")
                or path.endswith(".test.js")
                or path.endswith(".test.ts")
                or path.endswith(".test.tsx")
                or path.endswith(".spec.js")
                or path.endswith(".spec.ts")
                or path.endswith(".spec.tsx")
            )
        ]

        test_count = len(test_files)

        has_pytest_config = any(
            path in sampled_paths
            for path in {
                "pytest.ini",
                "pyproject.toml",
                "setup.cfg",
            }
        ) and (
            "pytest" in sampled_text
        )

        has_jest = (
            "jest" in sampled_text
            or any(
                "jest.config" in path
                for path in sampled_paths
            )
        )

        if test_count == 0:
            test_score = 20
            test_reasons.append(
                "No test files were detected."
            )

        elif test_count == 1:
            test_score = 45
            test_reasons.append(
                "1 automated test file detected."
            )

        elif test_count <= 3:
            test_score = 65
            test_reasons.append(
                f"{test_count} automated test files detected."
            )

        elif test_count <= 8:
            test_score = 80
            test_reasons.append(
                f"{test_count} automated test files detected."
            )

        else:
            test_score = 90
            test_reasons.append(
                f"{test_count}+ automated test files detected."
            )

        if has_pytest_config:
            test_score = min(100, test_score + 5)
            test_reasons.append(
                "Pytest configuration/dependency detected."
            )

        if has_jest:
            test_score = min(100, test_score + 5)
            test_reasons.append(
                "Jest configuration/dependency detected."
            )

        if test_score < 70:
            test_reasons.append(
                "Testing evidence is limited."
            )

        # ============================================================
        # 5. DEVOPS SCORE
        # ============================================================

        devops_score = 15
        devops_reasons = []

        has_dockerfile = any(
            path.endswith("dockerfile")
            for path in paths_set
        )

        has_compose = any(
            "docker-compose.yml" in path
            or "docker-compose.yaml" in path
            for path in paths_set
        )

        dockerfile_content = next(
            (
                content
                for path, content in sampled_files.items()
                if path.lower().endswith("dockerfile")
            ),
            "",
        ).lower()

        has_real_docker_evidence = (
            has_dockerfile
            or has_compose
            or "from python:" in sampled_text
            or "from node:" in sampled_text
        )

        has_ci = any(
            (
                ".github/workflows" in path
                or "ci" in path
                or "pipeline" in path
            )
            for path in paths_set
        )

        if has_real_docker_evidence:

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

        # Recommendations are deliberately repository-aware. A data/ML
        # notebook should not receive the same advice as a backend API.
        context_text = " ".join(
            [
                name,
                language or "",
                readme_lower,
                " ".join(paths_set),
                sampled_text,
            ]
        )

        data_ml_markers = (
            "machine learning",
            "data science",
            "data analytics",
            "prediction",
            "kaggle",
            "jupyter",
            "notebook",
            "pandas",
            "scikit-learn",
            "sklearn",
            "tensorflow",
            "pytorch",
            "xgboost",
            "catboost",
            "lightgbm",
        )

        frontend_markers = (
            "react",
            "next.js",
            "nextjs",
            "vue",
            "angular",
            "svelte",
            "frontend",
            "portfolio",
            "tailwind",
        )

        backend_markers = (
            "fastapi",
            "flask",
            "django",
            "express",
            "node.js",
            "nodejs",
            "spring",
            "api",
            "backend",
            "rest api",
            "postgres",
            "mysql",
        )

        # ============================================================
        # REPOSITORY TYPE CLASSIFICATION
        # ============================================================
        #
        # Prefer concrete stack/file evidence over generic README words.
        # For example, mentioning "API" in a README should not make a
        # portfolio or ML notebook a backend project.
        # ============================================================

        normalized_language = (language or "").lower()

        has_backend_framework = any(
            marker in context_text
            for marker in (
                "fastapi",
                "flask",
                "django",
                "express",
                "nestjs",
                "spring boot",
                "asp.net",
                "laravel",
                "rails",
            )
        )

        has_frontend_framework = any(
            marker in context_text
            for marker in (
                "react",
                "next.js",
                "nextjs",
                "vue",
                "angular",
                "svelte",
                "react native",
            )
        )

        has_ml_framework = any(
            marker in context_text
            for marker in (
                "scikit-learn",
                "sklearn",
                "tensorflow",
                "pytorch",
                "xgboost",
                "catboost",
                "lightgbm",
            )
        )

        has_notebook_evidence = any(
            path.endswith(".ipynb")
            for path in paths_set
        )

        has_ml_data_language = normalized_language in {
            "jupyter notebook",
            "r",
        }

        has_python = normalized_language == "python"

        has_node = (
            normalized_language in {"javascript", "typescript"}
            and any(
                marker in context_text
                for marker in (
                    "package.json",
                    "next",
                    "react",
                    "express",
                    "node",
                )
            )
        )

        is_data_ml = (
            has_ml_framework
            or has_notebook_evidence
            or has_ml_data_language
            or any(marker in context_text for marker in data_ml_markers)
        )

        is_frontend = (
            has_frontend_framework
            or has_node
        )

        is_backend = (
            has_backend_framework
            or (
                has_python
                and any(
                    marker in context_text
                    for marker in (
                        "requirements.txt",
                        "pyproject.toml",
                        "routes/",
                        "models/",
                        "services/",
                        "controllers/",
                        "api/",
                    )
                )
            )
        )

        # A repository can contain frontend + backend code.
        # In that case, backend-specific advice is still valid,
        # but ML/data classification gets priority.

        improvements = []

        if is_data_ml:
            if test_score < 70:
                improvements.append(
                    f"Move the core preprocessing/model logic in {name} into testable Python modules and add tests for data validation, feature engineering, and prediction behavior."
                )

            if doc_score < 80:
                improvements.append(
                    f"Document {name}'s dataset, target variable, feature engineering, evaluation metric, and reproducible run steps in the README."
                )

            if not any(
                marker in context_text
                for marker in ("requirements.txt", "pyproject.toml", "environment.yml", "pip install")
            ):
                improvements.append(
                    f"Add a reproducible dependency/environment definition to {name} so the analysis can be rerun consistently."
                )

            if not any(
                marker in context_text
                for marker in ("api", "fastapi", "flask", "streamlit", "gradio")
            ):
                improvements.append(
                    f"Add a small inference or prediction entry point to {name} so the model can be consumed outside the notebook."
                )

            if not has_ci:
                improvements.append(
                    f"Add a lightweight CI workflow for {name} that validates the Python environment and runs the project tests."
                )

        elif is_frontend and not is_backend:
            if test_score < 70:
                improvements.append(
                    f"Add component or end-to-end tests to {name} covering the main user flows."
                )

            if doc_score < 75:
                improvements.append(
                    f"Document the architecture, main user flows, local setup, and deployment process for {name}."
                )

            if not has_ci:
                improvements.append(
                    f"Add GitHub Actions to {name} for linting, type-checking, and production builds on every push."
                )

            if scale_score < 70:
                improvements.append(
                    f"Add measurable performance and accessibility checks to {name} and document the results."
                )

        elif is_backend:
            if test_score < 70:
                improvements.append(
                    f"Add API and service-layer tests to {name}, including success, validation, and failure paths."
                )

            if devops_score < 60:
                if not has_real_docker_evidence:
                    improvements.append(
                        f"Containerize {name} with a production-ready Dockerfile and a local Compose setup."
                    )

                if not has_ci:
                    improvements.append(
                        f"Add GitHub Actions to {name} to run tests and build checks automatically."
                    )

            if doc_score < 75:
                improvements.append(
                    f"Document {name}'s API architecture, environment variables, database setup, and deployment steps."
                )

            if scale_score < 70:
                improvements.append(
                    f"Add one evidence-backed production concern to {name}, such as caching, background jobs, rate limiting, or database indexing."
                )

        else:
            if test_score < 70:
                improvements.append(
                    f"Add automated tests that cover the most important workflows in {name}."
                )

            if doc_score < 75:
                improvements.append(
                    f"Expand {name}'s README with architecture, setup, usage, and deployment documentation."
                )

            if not has_ci:
                improvements.append(
                    f"Add a GitHub Actions workflow for {name} to automate the project's existing checks."
                )

            if devops_score < 60 and language and language.lower() not in {"jupyter notebook"}:
                improvements.append(
                    f"Add an appropriate deployment or packaging workflow to {name}."
                )

        # Keep recommendations concise and unique.
        improvements = list(dict.fromkeys(improvements))[:5]

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