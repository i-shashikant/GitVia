from __future__ import annotations

from collections import Counter
from typing import Any


class CareerAnalyzer:
    """
    Converts analyzed GitHub repository evidence into a deterministic
    developer career profile.

    No hardcoded career score is used.
    Everything is derived from repository metrics and detected technologies.
    """

    ROLE_REQUIREMENTS = {
        "Python Backend Developer": {
            "skills": {
                "Python": 1.0,
                "FastAPI": 1.0,
                "Flask": 0.9,
                "Django": 0.9,
                "SQL": 0.9,
                "PostgreSQL": 0.8,
                "REST API": 0.8,
                "Docker": 0.7,
                "Redis": 0.6,
                "Celery": 0.6,
                "Testing": 0.7,
            }
        },
        "Full Stack Developer": {
            "skills": {
                "JavaScript": 1.0,
                "TypeScript": 1.0,
                "React": 1.0,
                "Vue": 0.9,
                "Next.js": 0.9,
                "HTML": 0.7,
                "CSS": 0.7,
                "Python": 0.7,
                "SQL": 0.7,
                "Docker": 0.6,
            }
        },
        "AI / ML Engineer": {
            "skills": {
                "Python": 1.0,
                "Machine Learning": 1.0,
                "Pandas": 0.9,
                "NumPy": 0.9,
                "Scikit-learn": 0.9,
                "Jupyter": 0.8,
                "FastAPI": 0.7,
                "SQL": 0.6,
                "Docker": 0.6,
            }
        },
        "Data Scientist": {
            "skills": {
                "Python": 1.0,
                "Pandas": 1.0,
                "NumPy": 0.9,
                "Scikit-learn": 0.9,
                "Jupyter": 0.9,
                "SQL": 0.8,
                "Statistics": 0.7,
                "Machine Learning": 0.9,
            }
        },
        "Frontend Developer": {
            "skills": {
                "JavaScript": 1.0,
                "TypeScript": 1.0,
                "React": 1.0,
                "Vue": 0.9,
                "Next.js": 0.9,
                "HTML": 0.8,
                "CSS": 0.8,
            }
        },
    }

    def analyze(
        self,
        repositories: list[dict[str, Any]],
    ) -> dict[str, Any]:

        if not repositories:
            return self._empty_profile()

        skills = self._extract_skills(repositories)

        role_scores = {}

        for role, config in self.ROLE_REQUIREMENTS.items():
            role_scores[role] = self._calculate_role_score(
                skills,
                config["skills"],
            )

        ranked_roles = sorted(
            role_scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        primary_role = ranked_roles[0][0]
        secondary_role = (
            ranked_roles[1][0]
            if len(ranked_roles) > 1
            else None
        )

        current_level = self._determine_level(
            repositories
        )

        github_score = self._github_score(
            repositories
        )

        readiness_score = self._readiness_score(
            repositories,
            skills,
        )

        portfolio_score = self._portfolio_score(
            repositories
        )

        strongest_skills = self._strongest_skills(
            skills
        )

        weakest_skills = self._weakest_skills(
            skills
        )

        role_matches = []

        for role, score in ranked_roles:
            role_matches.append(
                {
                    "role": role,
                    "match_score": score,
                    "evidence": self._role_evidence(
                        role,
                        skills,
                    ),
                }
            )

        return {
            "primary_role": primary_role,
            "secondary_role": secondary_role,
            "current_level": current_level,

            "portfolio_score": portfolio_score,
            "github_score": github_score,
            "readiness_score": readiness_score,

            "skill_scores": skills,

            "strongest_skills": strongest_skills,
            "weakest_skills": weakest_skills,

            "role_matches": role_matches,

            "career_gaps": self._career_gaps(
                skills
            ),

            "recommended_actions": self._recommended_actions(
                repositories,
                skills,
            ),

            "repository_count": len(repositories),
        }

    # ---------------------------------------------------------
    # SKILL DETECTION
    # ---------------------------------------------------------

    def _extract_skills(
        self,
        repositories: list[dict[str, Any]],
    ) -> dict[str, int]:

        skill_counter = Counter()

        for repo in repositories:

            language = repo.get("language")

            if language:
                self._add_skill(
                    skill_counter,
                    language,
                )

            analysis = repo.get(
                "analysis"
            ) or {}

            text = str(
                repo.get("name", "")
            ) + " " + str(
                repo.get("description", "")
            )

            analysis_text = str(
                analysis
            )

            combined = (
                text + " " + analysis_text
            ).lower()

            skill_aliases = {
                "Python": [
                    "python",
                ],
                "JavaScript": [
                    "javascript",
                    "js",
                ],
                "TypeScript": [
                    "typescript",
                    "ts",
                ],
                "React": [
                    "react",
                ],
                "Vue": [
                    "vue",
                ],
                "Next.js": [
                    "next.js",
                    "nextjs",
                ],
                "FastAPI": [
                    "fastapi",
                ],
                "Flask": [
                    "flask",
                ],
                "Django": [
                    "django",
                ],
                "SQL": [
                    "sql",
                    "database",
                ],
                "PostgreSQL": [
                    "postgres",
                    "postgresql",
                ],
                "Redis": [
                    "redis",
                ],
                "Celery": [
                    "celery",
                ],
                "Docker": [
                    "docker",
                ],
                "Machine Learning": [
                    "machine learning",
                    "machine-learning",
                    "ml",
                ],
                "Pandas": [
                    "pandas",
                ],
                "NumPy": [
                    "numpy",
                    "np",
                ],
                "Scikit-learn": [
                    "scikit-learn",
                    "sklearn",
                ],
                "Jupyter": [
                    "jupyter",
                    "notebook",
                    "ipynb",
                ],
                "HTML": [
                    "html",
                ],
                "CSS": [
                    "css",
                ],
                "REST API": [
                    "rest api",
                    "restapi",
                    "/api/",
                ],
                "Statistics": [
                    "statistics",
                    "statistical",
                    "regression",
                ],
                "Testing": [
                    "testing",
                    "pytest",
                    "jest",
                    "unit test",
                    "integration test",
                ],
            }

            for skill, aliases in skill_aliases.items():

                if any(
                    alias in combined
                    for alias in aliases
                ):
                    self._add_skill(
                        skill_counter,
                        skill,
                    )

        return self._normalise_skill_scores(
            skill_counter,
            len(repositories),
        )

    def _add_skill(
        self,
        counter: Counter,
        skill: str,
    ) -> None:
        counter[skill] += 1

    def _normalise_skill_scores(
        self,
        counter: Counter,
        repository_count: int,
    ) -> dict[str, int]:

        if not counter:
            return {}

        scores = {}

        for skill, count in counter.items():

            # Multiple repositories demonstrate
            # stronger recurring evidence.
            score = min(
                100,
                35 + (
                    count / max(
                        repository_count,
                        1,
                    )
                ) * 65,
            )

            scores[skill] = round(
                score
            )

        return dict(
            sorted(
                scores.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        )

    # ---------------------------------------------------------
    # ROLE MATCHING
    # ---------------------------------------------------------

    def _calculate_role_score(
        self,
        skills: dict[str, int],
        requirements: dict[str, float],
    ) -> int:

        total_weight = sum(
            requirements.values()
        )

        if total_weight == 0:
            return 0

        achieved = 0.0

        for skill, weight in requirements.items():

            skill_score = skills.get(
                skill,
                0,
            )

            achieved += (
                (skill_score / 100)
                * weight
            )

        score = (
            achieved
            / total_weight
        ) * 100

        return round(
            min(100, score)
        )

    def _role_evidence(
        self,
        role: str,
        skills: dict[str, int],
    ) -> list[str]:

        requirements = (
            self.ROLE_REQUIREMENTS[role]["skills"]
        )

        evidence = []

        for skill in requirements:

            score = skills.get(
                skill,
                0,
            )

            if score >= 60:
                evidence.append(
                    f"{skill} evidence detected"
                )

        return evidence[:6]

    # ---------------------------------------------------------
    # OVERALL SCORES
    # ---------------------------------------------------------

    def _github_score(
        self,
        repositories: list[dict[str, Any]],
    ) -> int:

        scores = [
            float(
                repo.get(
                    "quality_score",
                    0,
                )
                or 0
            )
            for repo in repositories
        ]

        if not scores:
            return 0

        return round(
            sum(scores) / len(scores)
        )

    def _portfolio_score(
        self,
        repositories: list[dict[str, Any]],
    ) -> int:

        if not repositories:
            return 0

        scores = sorted(
            [
                float(
                    repo.get(
                        "quality_score",
                        0,
                    )
                    or 0
                )
                for repo in repositories
            ],
            reverse=True,
        )

        # Strong repositories contribute more
        # than unfinished / empty repositories.
        weights = []

        for index, score in enumerate(scores):
            if index == 0:
                weight = 3.0
            elif index < 4:
                weight = 2.0
            else:
                weight = 0.75

            weights.append(
                (score, weight)
            )

        numerator = sum(
            score * weight
            for score, weight in weights
        )

        denominator = sum(
            weight
            for _, weight in weights
        )

        return round(
            numerator / denominator
        )

    def _readiness_score(
        self,
        repositories: list[dict[str, Any]],
        skills: dict[str, int],
    ) -> int:

        if not repositories:
            return 0

        github_score = self._github_score(
            repositories
        )

        engineering_evidence = 0

        for skill in [
            "Python",
            "SQL",
            "FastAPI",
            "Docker",
            "Testing",
            "REST API",
            "PostgreSQL",
            "Redis",
        ]:
            if skills.get(skill, 0) >= 60:
                engineering_evidence += 1

        evidence_score = min(
            100,
            engineering_evidence * 12,
        )

        project_score = min(
            100,
            len(repositories) * 7,
        )

        readiness = (
            github_score * 0.50
            + evidence_score * 0.30
            + project_score * 0.20
        )

        return round(
            min(100, readiness)
        )

    # ---------------------------------------------------------
    # LEVEL
    # ---------------------------------------------------------

    def _determine_level(
        self,
        repositories: list[dict[str, Any]],
    ) -> str:

        github_score = self._github_score(
            repositories
        )

        strong_projects = sum(
            1
            for repo in repositories
            if float(
                repo.get(
                    "quality_score",
                    0,
                )
                or 0
            ) >= 70
        )

        if (
            github_score >= 80
            and strong_projects >= 3
        ):
            return "Advanced"

        if (
            github_score >= 60
            or strong_projects >= 2
        ):
            return "Intermediate"

        return "Developing"

    # ---------------------------------------------------------
    # STRENGTHS / GAPS
    # ---------------------------------------------------------

    def _strongest_skills(
        self,
        skills: dict[str, int],
    ) -> list[str]:

        return [
            skill
            for skill, score in skills.items()
            if score >= 65
        ][:6]

    def _weakest_skills(
        self,
        skills: dict[str, int],
    ) -> list[str]:

        important = [
            "Testing",
            "Docker",
            "AWS",
            "Redis",
            "Celery",
            "PostgreSQL",
        ]

        missing = [
            skill
            for skill in important
            if skills.get(skill, 0) < 60
        ]

        return missing[:6]

    def _career_gaps(
        self,
        skills: dict[str, int],
    ) -> list[dict[str, Any]]:

        gaps = []

        important_skills = {
            "Testing": 70,
            "Docker": 65,
            "AWS": 55,
            "Redis": 55,
            "PostgreSQL": 65,
            "Celery": 50,
        }

        for skill, target in important_skills.items():

            current = skills.get(
                skill,
                0,
            )

            if current < target:

                gaps.append(
                    {
                        "skill": skill,
                        "current_score": current,
                        "target_score": target,
                        "gap": target - current,
                    }
                )

        return gaps

    # ---------------------------------------------------------
    # ACTIONS
    # ---------------------------------------------------------

    def _recommended_actions(
        self,
        repositories: list[dict[str, Any]],
        skills: dict[str, int],
    ) -> list[str]:

        actions = []

        testing_count = sum(
            1
            for repo in repositories
            if (
                repo.get("analysis", {})
                .get("testing", {})
                .get("score", 0)
                >= 70
            )
        )

        if testing_count == 0:
            actions.append(
                "Add automated tests with Pytest or Jest to at least one flagship project."
            )

        docker_count = sum(
            1
            for repo in repositories
            if skills.get("Docker", 0) > 0
        )

        if docker_count == 0:
            actions.append(
                "Containerize a production-style project with Docker and Docker Compose."
            )

        if skills.get("PostgreSQL", 0) < 60:
            actions.append(
                "Showcase PostgreSQL database design in a backend project."
            )

        if skills.get("Redis", 0) < 60:
            actions.append(
                "Add Redis caching or background-job processing to a suitable backend project."
            )

        if skills.get("AWS", 0) < 60:
            actions.append(
                "Deploy one production project to a cloud platform and document the deployment."
            )

        if len(repositories) < 5:
            actions.append(
                "Build and maintain a small set of polished flagship repositories."
            )

        return actions[:6]

    def _empty_profile(self) -> dict[str, Any]:

        return {
            "primary_role": None,
            "secondary_role": None,
            "current_level": "Developing",
            "portfolio_score": 0,
            "github_score": 0,
            "readiness_score": 0,
            "skill_scores": {},
            "strongest_skills": [],
            "weakest_skills": [],
            "role_matches": [],
            "career_gaps": [],
            "recommended_actions": [],
            "repository_count": 0,
        }