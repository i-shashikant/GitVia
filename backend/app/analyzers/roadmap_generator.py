from typing import Any


class RoadmapGenerator:
    """
    Generates a deterministic, personalized roadmap from the user's
    actual GitHub-derived developer profile and target role.

    The roadmap is intentionally rule-based:
    - no fake scores
    - no fixed technology path
    - recommendations are driven by detected strengths/gaps
    """

    ROLE_SKILLS = {
        "Backend Engineer": [
            "Python",
            "FastAPI",
            "Flask",
            "SQL",
            "PostgreSQL",
            "REST API",
            "Docker",
            "Testing",
            "Redis",
            "CI/CD",
            "System Design",
        ],
        "Python Backend Developer": [
            "Python",
            "FastAPI",
            "Flask",
            "SQL",
            "PostgreSQL",
            "REST API",
            "Docker",
            "Testing",
            "Redis",
            "CI/CD",
            "System Design",
        ],
        "Frontend Developer": [
            "JavaScript",
            "TypeScript",
            "React",
            "Next.js",
            "HTML",
            "CSS",
            "Testing",
            "Performance",
            "Accessibility",
            "Deployment",
        ],
        "Full Stack Developer": [
            "JavaScript",
            "TypeScript",
            "React",
            "Next.js",
            "Python",
            "SQL",
            "REST API",
            "Docker",
            "Testing",
            "Deployment",
        ],
        "AI / ML Engineer": [
            "Python",
            "Machine Learning",
            "Pandas",
            "NumPy",
            "Scikit-learn",
            "FastAPI",
            "SQL",
            "Docker",
            "Testing",
            "Deployment",
        ],
        "Data Scientist": [
            "Python",
            "Pandas",
            "NumPy",
            "Scikit-learn",
            "Jupyter",
            "SQL",
            "Statistics",
            "Machine Learning",
            "Testing",
            "Deployment",
        ],
    }

    def generate_roadmap(
        self,
        dev_profile: dict[str, Any],
        user_repos: list[dict[str, Any]],
        target_role: str = "Backend Engineer",
    ) -> dict[str, Any]:

        strongest = list(dev_profile.get("strongest_skills") or [])
        weakest = list(dev_profile.get("weakest_skills") or [])
        skill_scores = dict(dev_profile.get("skill_scores") or {})

        # When Career sends us a stored job analysis, the JD becomes the
        # source of truth for the roadmap.  The normal role templates remain
        # available as a fallback for a standalone/general roadmap.
        job_required = self._deduplicate(
            dev_profile.get("job_required_skills") or []
        )
        job_preferred = self._deduplicate(
            dev_profile.get("job_preferred_skills") or []
        )
        job_missing = self._deduplicate(
            dev_profile.get("job_missing_skills") or []
        )

        job_specific = bool(job_required)

        if job_specific:
            role_skills = self._deduplicate(
                job_required + job_preferred
            )

            # Only expose strengths/improvement areas that are relevant to
            # this job.  This prevents unrelated GitHub skills from making
            # every job-specific roadmap look the same.
            required_lookup = {
                str(skill).lower() for skill in role_skills
            }

            job_strongest = [
                skill
                for skill in strongest
                if str(skill).lower() in required_lookup
            ]

            job_weakest = [
                skill
                for skill in weakest
                if str(skill).lower() in required_lookup
            ]

            # The persisted JobMatch/SkillGap is authoritative for explicit
            # missing skills, even when the base profile has no score entry.
            job_gaps = [
                skill
                for skill in job_missing
                if str(skill).lower() in required_lookup
            ]

            gaps = self._deduplicate(job_gaps)

            strongest_output = self._deduplicate(job_strongest)
            improving_output = self._deduplicate(job_weakest)

            # Classify the remaining job requirements using the same evidence
            # thresholds as the matcher, without turning moderate evidence
            # into a "missing" skill.
            for skill in role_skills:
                if skill in gaps or skill in strongest_output:
                    continue

                score = skill_scores.get(skill)

                if not isinstance(score, (int, float)):
                    gaps.append(skill)
                elif score < 45:
                    gaps.append(skill)
                elif score < 75 and skill not in improving_output:
                    improving_output.append(skill)

            gaps = self._deduplicate(gaps)
            improving_output = self._deduplicate(improving_output)

            # Preferred skills are useful secondary roadmap topics, but
            # required gaps always come first.
            roadmap_topics = self._prioritize_job_topics(
                gaps,
                improving_output,
                job_required,
                job_preferred,
            )
        else:
            role_key = self._resolve_role(target_role)
            role_skills = self.ROLE_SKILLS.get(
                role_key,
                self.ROLE_SKILLS["Backend Engineer"],
            )

            gaps = self._identify_gaps(
                role_skills,
                strongest,
                weakest,
                skill_scores,
            )

            roadmap_topics = self._prioritize_topics(
                gaps,
                role_skills,
                weakest,
            )

            strongest_output = strongest
            improving_output = weakest[:3]

        repo_name = (
            user_repos[0].get("name", "your existing project")
            if user_repos
            else "your existing project"
        )

        weekly_plan = []

        for index, topic in enumerate(roadmap_topics[:6], start=1):
            weekly_plan.append(
                self._build_week(
                    week_number=index,
                    topic=topic,
                    repo_name=repo_name,
                    target_role=target_role,
                )
            )

        return {
            "target_role": target_role,
            "duration_weeks": len(weekly_plan),
            "headline": (
                f"Job-specific {len(weekly_plan)}-Week Action Plan "
                f"for {target_role}"
                if job_specific
                else (
                    f"Personalized {len(weekly_plan)}-Week Action Plan "
                    f"for {target_role}"
                )
            ),
            "job_specific": job_specific,
            "strong_skills": strongest_output,
            "improving_skills": improving_output,
            "missing_skills": gaps,
            "weekly_plan": weekly_plan,
        }

    # ---------------------------------------------------------
    # ROLE RESOLUTION
    # ---------------------------------------------------------

    def _resolve_role(self, target_role: str) -> str:
        normalized = target_role.strip().lower()

        aliases = {
            "backend": "Backend Engineer",
            "backend developer": "Backend Engineer",
            "python backend": "Python Backend Developer",
            "python backend engineer": "Python Backend Developer",
            "frontend": "Frontend Developer",
            "frontend developer": "Frontend Developer",
            "full stack": "Full Stack Developer",
            "fullstack": "Full Stack Developer",
            "ai engineer": "AI / ML Engineer",
            "ml engineer": "AI / ML Engineer",
            "machine learning engineer": "AI / ML Engineer",
            "data scientist": "Data Scientist",
        }

        return aliases.get(normalized, target_role)

    # ---------------------------------------------------------
    # GAP DETECTION
    # ---------------------------------------------------------

    def _identify_gaps(
        self,
        role_skills: list[str],
        strongest: list[str],
        weakest: list[str],
        skill_scores: dict[str, Any],
    ) -> list[str]:

        strongest_text = " ".join(
            str(skill).lower() for skill in strongest
        )

        weakest_text = " ".join(
            str(skill).lower() for skill in weakest
        )

        gaps = []

        for skill in role_skills:
            score = skill_scores.get(skill)

            # Explicitly weak skill.
            if self._contains_skill(weakest_text, skill):
                gaps.append(skill)
                continue

            # Known score below a reasonable evidence threshold.
            if isinstance(score, (int, float)) and score < 65:
                gaps.append(skill)
                continue

            # No evidence of the skill.
            if score is None and not self._contains_skill(
                strongest_text,
                skill,
            ):
                gaps.append(skill)

        return self._deduplicate(gaps)

    # ---------------------------------------------------------
    # PRIORITIZATION
    # ---------------------------------------------------------

    def _prioritize_job_topics(
        self,
        gaps: list[str],
        improving: list[str],
        required_skills: list[str],
        preferred_skills: list[str],
    ) -> list[str]:
        """Prioritize topics from the actual job before generic fallback topics."""

        topics = []

        # 1. Explicit missing requirements are the highest priority.
        for skill in gaps:
            if skill not in topics:
                topics.append(skill)

        # 2. Then address weak/improving requirements from the same JD.
        for skill in improving:
            if skill not in topics:
                topics.append(skill)

        # 3. If the candidate is already strong, use remaining required
        # requirements to create evidence rather than inventing a new stack.
        for skill in required_skills:
            if skill not in topics:
                topics.append(skill)

        # 4. Preferred skills only fill remaining slots.
        for skill in preferred_skills:
            if skill not in topics:
                topics.append(skill)

        return self._deduplicate(topics)[:6]

    def _prioritize_topics(
        self,
        gaps: list[str],
        role_skills: list[str],
        weakest: list[str],
    ) -> list[str]:

        topics = []

        # Start with explicit gaps.
        for gap in gaps:
            if gap not in topics:
                topics.append(gap)

        # Add role-specific fundamentals if necessary.
        for skill in role_skills:
            if skill not in topics and len(topics) < 6:
                topics.append(skill)

        # Always finish with production/system-level evidence.
        if len(topics) < 6:
            for fallback in [
                "Testing",
                "Deployment",
                "System Design",
            ]:
                if fallback not in topics:
                    topics.append(fallback)

        return topics[:6]

    # ---------------------------------------------------------
    # WEEK GENERATION
    # ---------------------------------------------------------

    def _build_week(
        self,
        week_number: int,
        topic: str,
        repo_name: str,
        target_role: str,
    ) -> dict[str, Any]:

        plans = {
            "Docker": {
                "focus": "DevOps & Infrastructure",
                "title": "Production Containerization",
                "deliverable": (
                    f"Containerize {repo_name} with a production-ready "
                    "Docker setup."
                ),
                "guidance": (
                    "Use your existing project as evidence instead of "
                    "building another tutorial project."
                ),
                "tasks": [
                    "Create a production Dockerfile.",
                    "Optimize dependency installation and image layers.",
                    "Run the application locally inside the container.",
                ],
            },
            "Testing": {
                "focus": "Quality Assurance",
                "title": "Automated Testing",
                "deliverable": (
                    f"Build a meaningful automated test suite for "
                    f"{repo_name}."
                ),
                "guidance": (
                    "Prioritize API behavior, business logic, and "
                    "important failure cases."
                ),
                "tasks": [
                    "Add unit tests for core business logic.",
                    "Add API/integration tests for critical endpoints.",
                    "Run the test suite automatically before every push.",
                ],
            },
            "PostgreSQL": {
                "focus": "Database Engineering",
                "title": "PostgreSQL & Database Design",
                "deliverable": (
                    f"Move {repo_name} toward production-grade PostgreSQL "
                    "usage."
                ),
                "guidance": (
                    "Focus on schema design, indexes, transactions, and "
                    "real query behavior."
                ),
                "tasks": [
                    "Design normalized production database tables.",
                    "Add indexes for frequently queried fields.",
                    "Inspect and optimize important database queries.",
                ],
            },
            "SQL": {
                "focus": "Database Engineering",
                "title": "Advanced SQL",
                "deliverable": (
                    "Strengthen SQL skills through real application queries."
                ),
                "guidance": (
                    "Use your existing application's data model rather "
                    "than isolated SQL exercises."
                ),
                "tasks": [
                    "Write joins and aggregation queries.",
                    "Analyze query execution plans.",
                    "Add indexes and compare query performance.",
                ],
            },
            "FastAPI": {
                "focus": "Backend Engineering",
                "title": "FastAPI Production Patterns",
                "deliverable": (
                    f"Build production-quality FastAPI features inside "
                    f"{repo_name}."
                ),
                "guidance": (
                    "Focus on validation, dependency injection, errors, "
                    "and clean API boundaries."
                ),
                "tasks": [
                    "Add Pydantic request and response models.",
                    "Implement dependency-based authentication/authorization.",
                    "Document and test the API endpoints.",
                ],
            },
            "Flask": {
                "focus": "Backend Engineering",
                "title": "Flask Production Architecture",
                "deliverable": (
                    f"Strengthen the Flask architecture of {repo_name}."
                ),
                "guidance": (
                    "Improve modularity, configuration, error handling, "
                    "and API structure."
                ),
                "tasks": [
                    "Separate routes, services, and data access.",
                    "Add centralized error handling.",
                    "Add automated API tests.",
                ],
            },
            "Redis": {
                "focus": "Scalability & Performance",
                "title": "Redis & Caching",
                "deliverable": (
                    f"Introduce useful caching or background processing "
                    f"patterns into {repo_name}."
                ),
                "guidance": (
                    "Only cache data where repeated access justifies the "
                    "complexity."
                ),
                "tasks": [
                    "Identify an endpoint suitable for caching.",
                    "Implement Redis caching with an expiration policy.",
                    "Measure the response-time difference.",
                ],
            },
            "CI/CD": {
                "focus": "Automation",
                "title": "GitHub Actions CI",
                "deliverable": (
                    f"Create a CI pipeline for {repo_name}."
                ),
                "guidance": (
                    "Every pull request should automatically verify "
                    "the project."
                ),
                "tasks": [
                    "Create a GitHub Actions workflow.",
                    "Install dependencies and run tests.",
                    "Add lint/build/container verification.",
                ],
            },
            "Deployment": {
                "focus": "Cloud & Production",
                "title": "Production Deployment",
                "deliverable": (
                    f"Deploy {repo_name} and document the live system."
                ),
                "guidance": (
                    "The deployment should be reproducible and documented "
                    "for someone reviewing your GitHub profile."
                ),
                "tasks": [
                    "Configure production environment variables.",
                    "Deploy the application to a cloud platform.",
                    "Document the live URL and deployment process.",
                ],
            },
            "System Design": {
                "focus": "System Architecture",
                "title": "System Design & Architecture",
                "deliverable": (
                    f"Document the architecture and data flow of "
                    f"{repo_name}."
                ),
                "guidance": (
                    "Turn your existing project into evidence that you "
                    "understand architectural trade-offs."
                ),
                "tasks": [
                    "Create a system architecture diagram.",
                    "Document database, API, cache, and service boundaries.",
                    "Explain scalability and failure-handling trade-offs.",
                ],
            },
            "JavaScript": {
                "focus": "Frontend Engineering",
                "title": "Modern JavaScript",
                "deliverable": "Build production-quality frontend features.",
                "guidance": "Focus on maintainable application code.",
                "tasks": [
                    "Refactor one complex component into reusable logic.",
                    "Use modern async and state-management patterns.",
                    "Add tests for important user interactions.",
                ],
            },
            "TypeScript": {
                "focus": "Frontend Engineering",
                "title": "TypeScript",
                "deliverable": "Strengthen type safety across the frontend.",
                "guidance": "Replace implicit any and weak contracts with useful types.",
                "tasks": [
                    "Define API response interfaces.",
                    "Type component props and application state.",
                    "Remove avoidable any usage.",
                ],
            },
            "React": {
                "focus": "Frontend Engineering",
                "title": "React Application Architecture",
                "deliverable": "Improve React component architecture in an existing project.",
                "guidance": "Focus on reusable components and predictable state.",
                "tasks": [
                    "Extract reusable UI components.",
                    "Improve state and data-fetching boundaries.",
                    "Add loading and error states.",
                ],
            },
            "Next.js": {
                "focus": "Frontend Engineering",
                "title": "Next.js Production Patterns",
                "deliverable": "Build a production-ready Next.js feature.",
                "guidance": "Use routing, server/client boundaries, and performance patterns deliberately.",
                "tasks": [
                    "Improve route-level data fetching.",
                    "Add robust loading and error boundaries.",
                    "Optimize one page for production performance.",
                ],
            },
            "Python": {
                "focus": "Programming Fundamentals",
                "title": "Production Python",
                "deliverable": f"Refactor meaningful Python code in {repo_name}.",
                "guidance": "Focus on readability, modularity, typing, and maintainability.",
                "tasks": [
                    "Add type hints to important functions.",
                    "Refactor duplicated logic into reusable functions.",
                    "Add tests around the refactored code.",
                ],
            },
            "Machine Learning": {
                "focus": "Machine Learning Engineering",
                "title": "Production ML",
                "deliverable": "Turn an existing ML project into a reproducible pipeline.",
                "guidance": "Prioritize reproducibility and measurable evaluation.",
                "tasks": [
                    "Create a reproducible training pipeline.",
                    "Track evaluation metrics and validation methodology.",
                    "Expose the model through a documented interface.",
                ],
            },
        }

        language_topics = {
            "C": ("C Programming Foundations", "systems programming fundamentals"),
            "C++": ("C++ Engineering", "modern C++ and problem-solving"),
            "C#": ("C# Application Development", "modern C# application development"),
            ".NET": (".NET Backend Development", "ASP.NET Core and the .NET ecosystem"),
            "Java": ("Java Backend Development", "modern Java and production backend patterns"),
            "JavaScript": ("Modern JavaScript", "production JavaScript"),
            "TypeScript": ("TypeScript", "strong typing and maintainable application contracts"),
            "Go": ("Go Backend Development", "idiomatic Go services"),
            "Rust": ("Rust Engineering", "safe systems-oriented Rust development"),
            "PHP": ("PHP Application Development", "modern PHP application development"),
            "Ruby": ("Ruby Application Development", "maintainable Ruby application development"),
            "Kotlin": ("Kotlin Development", "modern Kotlin application development"),
            "Swift": ("Swift Development", "modern Swift application development"),
            "Dart": ("Dart Development", "Dart application development"),
            "Scala": ("Scala Development", "Scala application development"),
            "R": ("R & Data Analysis", "R-based data analysis"),
            "SQL": ("Advanced SQL", "production SQL and query design"),
            "PL/SQL": ("PL/SQL", "database-side programming"),
            "T-SQL": ("T-SQL", "SQL Server development"),
            "Bash": ("Shell Automation", "reliable Bash automation"),
            "PowerShell": ("PowerShell Automation", "Windows and cloud automation"),
        }

        if topic in language_topics:
            language_title, language_focus = language_topics[topic]
            plan = {
                "focus": "Programming & Engineering",
                "title": language_title,
                "deliverable": (
                    f"Create concrete {topic} evidence aligned with "
                    f"the {target_role} job."
                ),
                "guidance": (
                    f"Focus on {language_focus}. Build something small but "
                    "real, test it, and document the implementation."
                ),
                "tasks": [
                    f"Learn the production fundamentals of {topic} required by the job.",
                    f"Implement a meaningful {topic} feature or small service.",
                    f"Add tests and document the {topic} implementation in the README.",
                ],
            }
        elif topic == "MySQL":
            plan = {
                "focus": "Database Engineering",
                "title": "MySQL Application Database",
                "deliverable": f"Add meaningful MySQL evidence to {repo_name}.",
                "guidance": "Focus on schema design, joins, indexes, transactions, and application integration.",
                "tasks": [
                    "Design or adapt a relational schema for the project.",
                    "Implement application queries with joins, constraints, and indexes.",
                    "Test the database integration and document the schema.",
                ],
            }
        elif topic == "Node.js":
            plan = {
                "focus": "Backend Engineering",
                "title": "Node.js Backend Evidence",
                "deliverable": f"Build a small production-style Node.js service or feature.",
                "guidance": "Focus on API design, async execution, validation, errors, and testing.",
                "tasks": [
                    "Create a Node.js API endpoint with validation.",
                    "Add error handling and automated API tests.",
                    "Document how the service is run and deployed.",
                ],
            }
        elif topic in {"HTML", "CSS"}:
            plan = {
                "focus": "Frontend Engineering",
                "title": f"{topic} Production UI",
                "deliverable": f"Create job-aligned {topic} evidence inside {repo_name}.",
                "guidance": "Improve a real interface rather than creating an isolated tutorial page.",
                "tasks": [
                    f"Implement a meaningful UI feature using {topic}.",
                    "Make the implementation responsive and accessible.",
                    "Document the feature and verify it in the deployed application.",
                ],
            }
        else:
            plan = plans.get(
                topic,
                {
                "focus": f"{target_role} Skill Development",
                "title": f"{topic} Development",
                "deliverable": (
                    f"Build practical {topic} evidence using "
                    f"{repo_name}."
                ),
                "guidance": (
                    f"Strengthen {topic} through a concrete feature "
                    "in an existing project."
                ),
                "tasks": [
                    f"Study the core production concepts of {topic}.",
                    f"Implement {topic} in an existing project.",
                    f"Document the {topic} implementation in the README.",
                ],
            },
        )

        return {
            "week": week_number,
            "title": plan["title"],
            "focus": plan["focus"],
            "status": (
                "In Progress"
                if week_number == 1
                else "Upcoming"
            ),
            "deliverable": plan["deliverable"],
            "guidance": plan["guidance"],
            "tasks": [
                {
                    "title": task,
                    "description": plan["guidance"],
                    "skills": [topic],
                    "estimated_hours": 4,
                }
                for task in plan["tasks"]
            ],
        }

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------

    @staticmethod
    def _contains_skill(text: str, skill: str) -> bool:
        return skill.lower() in text.lower()

    @staticmethod
    def _deduplicate(items: list[str]) -> list[str]:
        seen = set()
        result = []

        for item in items:
            if item not in seen:
                seen.add(item)
                result.append(item)

        return result