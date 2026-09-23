from __future__ import annotations

from collections import defaultdict
from typing import Any


class CareerAnalyzer:
    """
    Evidence-based developer career analyzer.

    Scores are derived from:
    - repository languages
    - repository technology stacks
    - structured repository analysis
    - repository quality scores
    - engineering dimensions
    - repeated technology evidence

    The analyzer does NOT award skill points simply because a technology
    appears in an arbitrary recommendation or sentence.
    """

    # ---------------------------------------------------------
    # ROLE REQUIREMENTS
    # ---------------------------------------------------------

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

    # Aliases are used against explicit repository evidence.
    SKILL_ALIASES = {
        "Python": ["python", "python3"],
        "JavaScript": ["javascript", "js"],
        "TypeScript": ["typescript", "ts"],
        "React": ["react", "reactjs"],
        "Vue": ["vue", "vuejs"],
        "Next.js": ["next.js", "nextjs"],
        "FastAPI": ["fastapi"],
        "Flask": ["flask"],
        "Django": ["django"],
        "SQL": ["sql", "sqlite", "mysql", "postgres", "postgresql"],
        "PostgreSQL": ["postgresql", "postgres"],
        "Redis": ["redis"],
        "Celery": ["celery"],
        "Docker": ["docker", "dockerfile", "docker compose", "docker-compose"],
        "AWS": [
            "aws",
            "amazon web services",
            "ec2",
            "s3",
            "lambda",
            "ecs",
            "eks",
            "rds",
            "cloudfront",
        ],
        "Machine Learning": [
            "machine learning",
            "machine-learning",
            "ml",
            "classification",
            "regression",
            "clustering",
        ],
        "Pandas": ["pandas"],
        "NumPy": ["numpy", "np"],
        "Scikit-learn": ["scikit-learn", "sklearn"],
        "Jupyter": ["jupyter", "notebook", "ipynb"],
        "HTML": ["html"],
        "CSS": ["css"],
        "REST API": ["rest api", "restapi", "/api/"],
        "Statistics": [
            "statistics",
            "statistical",
            "regression",
            "hypothesis testing",
            "probability",
        ],
        "Testing": [
            "pytest",
            "jest",
            "unittest",
            "unit test",
            "integration test",
            "test suite",
            "automated test",
        ],
    }

    # ---------------------------------------------------------
    # PUBLIC API
    # ---------------------------------------------------------

    def analyze(
        self,
        repositories: list[dict[str, Any]],
    ) -> dict[str, Any]:

        if not repositories:
            return self._empty_profile()

        skills = self._extract_skills(repositories)

        role_scores: dict[str, int] = {}

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

        github_score = self._github_score(repositories)

        portfolio_score = self._portfolio_score(repositories)

        readiness_score = self._readiness_score(
            repositories,
            skills,
        )

        current_level = self._determine_level(
            repositories,
            github_score,
            readiness_score,
        )

        strongest_skills = self._strongest_skills(skills)
        weakest_skills = self._weakest_skills(skills)

        role_matches = []

        for role, score in ranked_roles:
            role_matches.append(
                {
                    "role": role,
                    "match_score": score,
                    "evidence": self._role_evidence(
                        role,
                        skills,
                        repositories,
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

            "career_gaps": self._career_gaps(skills),

            "recommended_actions": self._recommended_actions(
                repositories,
                skills,
            ),

            "repository_count": len(repositories),
        }

    # ---------------------------------------------------------
    # EVIDENCE EXTRACTION
    # ---------------------------------------------------------

    def _extract_skills(
        self,
        repositories: list[dict[str, Any]],
    ) -> dict[str, int]:
        """
        Build skill scores from repository evidence.

        Evidence strength:

        100 -> explicit language / tech_stack evidence
         80 -> structured analyzer evidence
         50 -> repository metadata evidence

        Repeated evidence across repositories increases confidence.
        """

        evidence: dict[str, list[int]] = defaultdict(list)

        for repo in repositories:
            analysis = repo.get("analysis") or {}

            # -------------------------------------------------
            # STRONGEST SOURCE: language
            # -------------------------------------------------

            language = self._normalise_text(repo.get("language"))

            if language:
                for skill in self._skills_matching_text(language):
                    evidence[skill].append(100)

            # -------------------------------------------------
            # STRONG SOURCE: tech_stack
            # -------------------------------------------------

            tech_stack = repo.get("tech_stack") or []

            if isinstance(tech_stack, str):
                tech_stack = [tech_stack]

            if isinstance(tech_stack, list):
                for technology in tech_stack:
                    technology_text = self._normalise_text(technology)

                    if not technology_text:
                        continue

                    for skill in self._skills_matching_text(
                        technology_text
                    ):
                        evidence[skill].append(100)

            # -------------------------------------------------
            # STRONG SOURCE: structured analysis
            # -------------------------------------------------

            structured_evidence = self._structured_analysis_text(
                analysis
            )

            for skill in self._skills_matching_text(
                structured_evidence
            ):
                evidence[skill].append(80)

            # -------------------------------------------------
            # MODERATE SOURCE: repo metadata
            # -------------------------------------------------

            metadata = " ".join(
                [
                    self._normalise_text(repo.get("name")),
                    self._normalise_text(repo.get("description")),
                ]
            )

            for skill in self._skills_matching_text(metadata):
                evidence[skill].append(50)

        return self._normalise_skill_scores(
            evidence,
            len(repositories),
        )

    def _skills_matching_text(
        self,
        text: str,
    ) -> set[str]:

        if not text:
            return set()

        text = text.lower()

        matched = set()

        for skill, aliases in self.SKILL_ALIASES.items():
            for alias in aliases:
                if self._contains_term(text, alias):
                    matched.add(skill)
                    break

        return matched

    @staticmethod
    def _contains_term(
        text: str,
        term: str,
    ) -> bool:

        term = term.lower().strip()

        if not term:
            return False

        # For path-like/API terms, substring matching is appropriate.
        if "/" in term or "-" in term or "." in term:
            return term in text

        # Normal word boundary matching.
        import re

        return bool(
            re.search(
                rf"\b{re.escape(term)}\b",
                text,
            )
        )

    def _structured_analysis_text(
        self,
        analysis: dict[str, Any],
    ) -> str:
        """
        Only inspect useful structured analysis fields.

        We deliberately avoid:
            str(analysis)

        because that can turn recommendations such as
        "Consider adding Docker" into false Docker evidence.
        """

        fields = [
            "tech_stack",
            "technologies",
            "frameworks",
            "libraries",
            "tools",
            "languages",
            "detected_technologies",
            "detected_tools",
            "architecture_summary",
            "summary",
        ]

        values: list[str] = []

        for field in fields:
            value = analysis.get(field)

            if value is None:
                continue

            if isinstance(value, list):
                values.extend(
                    str(item)
                    for item in value
                )
            elif isinstance(value, dict):
                values.extend(
                    str(key)
                    for key in value.keys()
                )
                values.extend(
                    str(item)
                    for item in value.values()
                    if isinstance(item, (str, int, float))
                )
            elif isinstance(value, (str, int, float)):
                values.append(str(value))

        return " ".join(values)

    def _normalise_skill_scores(
        self,
        evidence: dict[str, list[int]],
        repository_count: int,
    ) -> dict[str, int]:

        if not evidence:
            return {}

        scores: dict[str, int] = {}

        for skill, values in evidence.items():
            if not values:
                continue

            # Keep only the strongest piece of evidence from each
            # repository/source rather than blindly stacking mentions.
            strongest = max(values)

            # Strong evidence establishes the baseline.
            if strongest >= 100:
                base = 70
            elif strongest >= 80:
                base = 55
            else:
                base = 35

            # Diminishing returns:
            # 1 occurrence  -> +0
            # 2 occurrences -> +8
            # 3 occurrences -> +14
            # 4 occurrences -> +19
            # 5+ occurrences -> capped at +24
            occurrence_count = len(values)

            recurrence_bonus = min(
                24,
                round(
                    10 * (
                        1 - (
                            1 / (
                                occurrence_count + 0.5
                            )
                        )
                    ) * 3
                ),
            )

            score = base + recurrence_bonus

            # Broad repository coverage gives a small additional
            # confidence bonus.
            if repository_count >= 5 and occurrence_count >= 3:
                score += 3

            if repository_count >= 10 and occurrence_count >= 5:
                score += 3

            scores[skill] = min(
                95,
                round(score),
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

        total_weight = sum(requirements.values())

        if total_weight == 0:
            return 0

        achieved = 0.0

        for skill, weight in requirements.items():
            skill_score = skills.get(skill, 0)

            achieved += (
                (skill_score / 100)
                * weight
            )

        score = (
            achieved / total_weight
        ) * 100

        return round(
            min(100, score)
        )

    def _role_evidence(
        self,
        role: str,
        skills: dict[str, int],
        repositories: list[dict[str, Any]],
    ) -> list[str]:

        requirements = (
            self.ROLE_REQUIREMENTS[role]["skills"]
        )

        evidence = []

        for skill in requirements:
            score = skills.get(skill, 0)

            if score >= 80:
                evidence.append(
                    f"Strong {skill} evidence"
                )
            elif score >= 60:
                evidence.append(
                    f"Demonstrated {skill} experience"
                )

        return evidence[:6]

    # ---------------------------------------------------------
    # GITHUB SCORE
    # ---------------------------------------------------------

    def _github_score(
        self,
        repositories: list[dict[str, Any]],
    ) -> int:

        if not repositories:
            return 0

        quality_scores = []

        for repo in repositories:
            quality = float(
                repo.get("quality_score", 0)
                or 0
            )

            quality_scores.append(
                max(0, min(100, quality))
            )

        if not quality_scores:
            return 0

        average_quality = (
            sum(quality_scores)
            / len(quality_scores)
        )

        # Breadth is useful, but deliberately capped.
        breadth_bonus = min(
            10,
            len(repositories) * 2,
        )

        return round(
            min(
                100,
                average_quality + breadth_bonus,
            )
        )

    # ---------------------------------------------------------
    # PORTFOLIO SCORE
    # ---------------------------------------------------------

    def _portfolio_score(
        self,
        repositories: list[dict[str, Any]],
    ) -> int:

        if not repositories:
            return 0

        scores = sorted(
            [
                float(
                    repo.get("quality_score", 0)
                    or 0
                )
                for repo in repositories
            ],
            reverse=True,
        )

        # Strong projects contribute more than unfinished ones.
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

        if denominator == 0:
            return 0

        return round(
            numerator / denominator
        )

    # ---------------------------------------------------------
    # READINESS
    # ---------------------------------------------------------

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

        # Engineering capabilities.
        engineering_skills = [
            "Python",
            "SQL",
            "REST API",
            "Docker",
            "Testing",
            "PostgreSQL",
            "Redis",
            "AWS",
        ]

        engineering_values = [
            skills.get(skill, 0)
            for skill in engineering_skills
        ]

        engineering_score = (
            sum(engineering_values)
            / len(engineering_values)
        )

        # Project quality.
        portfolio_score = self._portfolio_score(
            repositories
        )

        # Testing / DevOps / production evidence.
        production_skills = [
            skills.get("Testing", 0),
            skills.get("Docker", 0),
            skills.get("PostgreSQL", 0),
            skills.get("AWS", 0),
            skills.get("Redis", 0),
        ]

        production_score = (
            sum(production_skills)
            / len(production_skills)
        )

        readiness = (
            github_score * 0.35
            + portfolio_score * 0.30
            + engineering_score * 0.20
            + production_score * 0.15
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
        github_score: int,
        readiness_score: int,
    ) -> str:

        strong_projects = sum(
            1
            for repo in repositories
            if float(
                repo.get("quality_score", 0)
                or 0
            ) >= 70
        )

        if (
            github_score >= 82
            and readiness_score >= 80
            and strong_projects >= 3
        ):
            return "Advanced"

        if (
            github_score >= 60
            and readiness_score >= 55
        ) or strong_projects >= 2:
            return "Intermediate"

        return "Developing"

    # ---------------------------------------------------------
    # STRENGTHS
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

    # ---------------------------------------------------------
    # WEAKNESSES
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # CAREER GAPS
    # ---------------------------------------------------------

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

        return sorted(
            gaps,
            key=lambda item: item["gap"],
            reverse=True,
        )

    # ---------------------------------------------------------
    # RECOMMENDATIONS
    # ---------------------------------------------------------

    def _recommended_actions(
        self,
        repositories: list[dict[str, Any]],
        skills: dict[str, int],
    ) -> list[str]:

        actions = []

        # Testing
        testing_count = sum(
            1
            for repo in repositories
            if (
                (repo.get("analysis") or {})
                .get("testing", {})
                .get("score", 0)
                >= 70
            )
        )

        if testing_count == 0:
            actions.append(
                "Add automated tests with Pytest or Jest to at least one flagship project."
            )

        # Docker
        if skills.get("Docker", 0) < 60:
            actions.append(
                "Containerize a production-style project with Docker and Docker Compose."
            )

        # PostgreSQL
        if skills.get("PostgreSQL", 0) < 60:
            actions.append(
                "Showcase PostgreSQL database design in a backend project."
            )

        # Redis
        if skills.get("Redis", 0) < 60:
            actions.append(
                "Add Redis caching or background-job processing to a suitable backend project."
            )

        # AWS
        if skills.get("AWS", 0) < 60:
            actions.append(
                "Deploy one production project to a cloud platform and document the deployment."
            )

        # Portfolio breadth
        if len(repositories) < 3:
            actions.append(
                "Build and maintain a small set of polished flagship repositories."
            )

        return actions[:6]

    # ---------------------------------------------------------
    # EMPTY PROFILE
    # ---------------------------------------------------------

    def _empty_profile(
        self,
    ) -> dict[str, Any]:

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

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------

    @staticmethod
    def _normalise_text(
        value: Any,
    ) -> str:

        if value is None:
            return ""

        return str(value).strip().lower()