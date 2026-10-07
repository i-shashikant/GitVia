from __future__ import annotations

import re
from typing import Any


class JobAnalyzer:
    """
    Deterministic job-description analyzer.

    Extracts technical requirements from a JD and compares them against
    the developer's existing GitHub evidence.

    Scores are intentionally deterministic:
    - required skills carry more weight
    - preferred skills carry less weight
    - GitHub evidence is taken from structured profile/repository data
    - missing skills are explicit
    """

    SKILL_ALIASES: dict[str, tuple[str, ...]] = {
        # Programming languages
        "Python": ("python",),
        "Java": ("java",),
        "JavaScript": ("javascript", "js"),
        "TypeScript": ("typescript", "ts"),
        "C": ("c",),
        "C++": ("c++", "cpp", "c plus plus", "c+"),
        "C#": ("c#", "c sharp", "c-sharp"),
        ".NET": (".net", "dotnet", "dot net"),
        "Go": ("golang", "go"),
        "Rust": ("rust",),
        "PHP": ("php",),
        "Ruby": ("ruby",),
        "Kotlin": ("kotlin",),
        "Swift": ("swift",),
        "Dart": ("dart",),
        "Scala": ("scala",),
        "R": ("r",),
        "MATLAB": ("matlab",),
        "Perl": ("perl",),
        "Lua": ("lua",),
        "Groovy": ("groovy",),
        "Julia": ("julia",),
        "Haskell": ("haskell",),
        "Elixir": ("elixir",),
        "Erlang": ("erlang",),
        "Clojure": ("clojure",),
        "Objective-C": ("objective-c", "objective c"),
        "Assembly": ("assembly", "assembler", "asm"),
        "Solidity": ("solidity",),
        "SQL": ("sql",),
        "PL/SQL": ("pl/sql", "plsql"),
        "T-SQL": ("t-sql", "tsql", "transact-sql"),
        "Bash": ("bash", "shell scripting", "shell script"),
        "PowerShell": ("powershell", "power shell"),

        # Frontend / web
        "React": ("react", "react.js", "reactjs"),
        "React Native": ("react native",),
        "Next.js": ("next.js", "nextjs", "next js"),
        "Vue": ("vue", "vue.js", "vuejs"),
        "Nuxt": ("nuxt", "nuxt.js", "nuxtjs"),
        "Angular": ("angular", "angular.js", "angularjs"),
        "Svelte": ("svelte",),
        "SvelteKit": ("sveltekit",),
        "HTML": ("html", "html5"),
        "CSS": ("css", "css3"),
        "Tailwind CSS": ("tailwind", "tailwind css", "tailwindcss"),
        "Bootstrap": ("bootstrap",),
        "Material UI": ("material ui", "mui"),
        "jQuery": ("jquery",),
        "Redux": ("redux",),
        "Zustand": ("zustand",),
        "Vite": ("vite",),
        "Webpack": ("webpack",),
        "Babel": ("babel",),
        "Three.js": ("three.js", "threejs", "three js"),
        "WebGL": ("webgl",),
        "GSAP": ("gsap",),
        "Framer Motion": ("framer motion",),
        "Responsive Design": ("responsive design", "responsive web design"),
        "Accessibility": ("accessibility", "a11y"),
        "Web Performance": ("web performance", "frontend performance"),

        # Backend / APIs / frameworks
        "Flask": ("flask",),
        "FastAPI": ("fastapi", "fast api"),
        "Django": ("django",),
        "Node.js": ("node.js", "nodejs", "node js"),
        "Express": ("express.js", "expressjs", "express"),
        "NestJS": ("nestjs", "nest.js", "nest js"),
        "Fastify": ("fastify",),
        "Spring": ("spring framework", "spring"),
        "Spring Boot": ("spring boot",),
        "ASP.NET": ("asp.net", "asp net", "aspnet"),
        "ASP.NET Core": ("asp.net core", "aspnet core"),
        "Entity Framework": ("entity framework", "ef core", "entity framework core"),
        "Laravel": ("laravel",),
        "Symfony": ("symfony",),
        "Ruby on Rails": ("ruby on rails", "rails"),
        "Gin": ("gin-gonic", "gin framework",),
        "Echo": ("echo framework",),
        "Phoenix": ("phoenix framework",),
        "REST API": ("rest api", "restful api", "restful", "rest apis"),
        "GraphQL": ("graphql",),
        "gRPC": ("grpc", "g-rpc"),
        "WebSockets": ("websocket", "websockets", "web sockets"),
        "OpenAPI": ("openapi", "open api"),
        "Swagger": ("swagger",),
        "OAuth": ("oauth", "oauth2", "oauth 2.0"),
        "JWT": ("jwt", "json web token", "json web tokens"),
        "Microservices": ("microservices", "microservices architecture"),
        "Serverless": ("serverless",),
        "Event-Driven Architecture": ("event-driven architecture", "event driven architecture"),
        "Message Queues": ("message queue", "message queues", "mq"),

        # Databases / data platforms
        "PostgreSQL": ("postgresql", "postgres"),
        "MySQL": ("mysql",),
        "SQLite": ("sqlite",),
        "SQL Server": ("sql server", "mssql", "ms sql"),
        "Oracle": ("oracle database", "oracle db", "oracle"),
        "MariaDB": ("mariadb",),
        "MongoDB": ("mongodb", "mongo db", "mongo"),
        "Redis": ("redis",),
        "Cassandra": ("cassandra",),
        "DynamoDB": ("dynamodb", "dynamo db"),
        "Firebase": ("firebase",),
        "Firestore": ("firestore",),
        "Supabase": ("supabase",),
        "Neo4j": ("neo4j", "neo4j graph"),
        "Elasticsearch": ("elasticsearch", "elastic search"),
        "OpenSearch": ("opensearch", "open search"),
        "Snowflake": ("snowflake",),
        "BigQuery": ("bigquery", "big query"),
        "Databricks": ("databricks",),
        "Apache Spark": ("apache spark", "spark"),
        "Kafka": ("kafka", "apache kafka"),
        "RabbitMQ": ("rabbitmq", "rabbit mq"),
        "Celery": ("celery",),
        "ETL": ("etl", "extract transform load"),
        "Data Warehousing": ("data warehouse", "data warehousing"),

        # Cloud / DevOps / infrastructure
        "Docker": ("docker", "dockerfile", "docker compose", "docker-compose"),
        "Kubernetes": ("kubernetes", "k8s", "kubernates"),
        "Helm": ("helm", "helm charts"),
        "Terraform": ("terraform",),
        "Ansible": ("ansible",),
        "Pulumi": ("pulumi",),
        "Jenkins": ("jenkins",),
        "GitHub Actions": ("github actions", "github action"),
        "GitLab CI": ("gitlab ci", "gitlab-ci"),
        "CircleCI": ("circleci", "circle ci"),
        "Argo CD": ("argo cd", "argocd"),
        "Prometheus": ("prometheus",),
        "Grafana": ("grafana",),
        "Nginx": ("nginx",),
        "AWS": ("aws", "amazon web services"),
        "Azure": ("azure", "microsoft azure"),
        "GCP": ("gcp", "google cloud", "google cloud platform"),
        "AWS EC2": ("ec2", "amazon ec2"),
        "AWS S3": ("s3", "amazon s3"),
        "AWS Lambda": ("aws lambda", "lambda"),
        "AWS RDS": ("aws rds", "rds"),
        "Google Cloud Run": ("cloud run", "google cloud run"),
        "CI/CD": ("ci/cd", "cicd", "continuous integration", "continuous delivery", "continuous deployment"),
        "Deployment": ("deployment", "deployments", "production deployment"),
        "IaC": ("iac", "infrastructure as code"),
        "Linux": ("linux",),
        "Git": ("git",),
        "GitHub": ("github",),
        "GitLab": ("gitlab",),

        # Testing / quality
        "Testing": ("software testing", "testing", "automated testing", "test automation"),
        "Unit Testing": ("unit testing", "unit tests"),
        "Integration Testing": ("integration testing", "integration tests"),
        "Pytest": ("pytest",),
        "Jest": ("jest",),
        "Mocha": ("mocha",),
        "Cypress": ("cypress",),
        "Playwright": ("playwright",),
        "Selenium": ("selenium",),
        "JUnit": ("junit",),
        "TestNG": ("testng",),
        "Postman": ("postman",),
        "TDD": ("tdd", "test-driven development", "test driven development"),
        "Debugging": ("debugging", "debug"),

        # Data / ML / AI
        "Machine Learning": ("machine learning", "ml"),
        "Deep Learning": ("deep learning",),
        "Artificial Intelligence": ("artificial intelligence", "ai"),
        "Generative AI": ("generative ai", "genai", "gen ai"),
        "NLP": ("nlp", "natural language processing"),
        "Computer Vision": ("computer vision",),
        "Statistics": ("statistics", "statistical analysis"),
        "Data Analysis": ("data analysis", "data analytics"),
        "Scikit-learn": ("scikit-learn", "sklearn"),
        "Pandas": ("pandas",),
        "NumPy": ("numpy",),
        "SciPy": ("scipy",),
        "TensorFlow": ("tensorflow",),
        "PyTorch": ("pytorch",),
        "Keras": ("keras",),
        "XGBoost": ("xgboost",),
        "LightGBM": ("lightgbm", "light gbm"),
        "CatBoost": ("catboost",),
        "Jupyter": ("jupyter", "jupyter notebook"),
        "Hugging Face": ("hugging face", "huggingface"),
        "Transformers": ("transformers", "huggingface transformers"),
        "LangChain": ("langchain",),
        "LlamaIndex": ("llamaindex", "llama index"),
        "LLMs": ("llm", "llms", "large language model", "large language models"),
        "OpenAI": ("openai",),
        "Gemini": ("gemini", "google gemini"),
        "Claude": ("claude", "anthropic claude"),
        "RAG": ("rag", "retrieval augmented generation", "retrieval-augmented generation"),
        "Vector Databases": ("vector database", "vector databases", "vector db", "vector dbs"),
        "FAISS": ("faiss",),
        "Pinecone": ("pinecone",),
        "ChromaDB": ("chromadb", "chroma db"),
        "MLflow": ("mlflow",),
        "MLOps": ("mlops", "ml ops"),

        # Core engineering / architecture
        "Object-Oriented Programming": ("object-oriented programming", "object oriented programming", "oop"),
        "Data Structures": ("data structures", "data structure"),
        "Algorithms": ("algorithms", "algorithm"),
        "System Design": ("system design", "distributed systems", "software architecture"),
        "Design Patterns": ("design patterns",),
        "SOLID": ("solid principles", "solid design", "solid"),
        "Clean Architecture": ("clean architecture",),
        "Domain-Driven Design": ("domain-driven design", "ddd"),
        "API Design": ("api design",),
        "Performance Optimization": ("performance optimization", "performance tuning"),
        "Security": ("application security", "web security", "cybersecurity", "security"),
        "SDLC": ("sdlc", "software development life cycle"),

        # Mobile / specialized
        "Flutter": ("flutter",),
        "Android": ("android", "android development"),
        "iOS": ("ios", "ios development"),
        "SwiftUI": ("swiftui",),
        "Jetpack Compose": ("jetpack compose",),
        "Xamarin": ("xamarin",),
        ".NET MAUI": (".net maui", "dotnet maui"),
        "Unity": ("unity",),
        "Unreal Engine": ("unreal engine", "unreal"),
        "Blockchain": ("blockchain",),
        "Web3": ("web3", "web 3"),
        "Solidity": ("solidity",),
    }

    DEVOPS_SKILLS = {
        "Docker",
        "Kubernetes",
        "Helm",
        "Terraform",
        "Ansible",
        "Pulumi",
        "Jenkins",
        "GitHub Actions",
        "GitLab CI",
        "CircleCI",
        "Argo CD",
        "Prometheus",
        "Grafana",
        "Nginx",
        "AWS",
        "Azure",
        "GCP",
        "AWS EC2",
        "AWS S3",
        "AWS Lambda",
        "AWS RDS",
        "Google Cloud Run",
        "CI/CD",
        "IaC",
        "Linux",
    }

    ENGINEERING_SKILLS = set(SKILL_ALIASES) - {
        "English Proficiency",
        "Project Management",
        "Product Development",
        "PLM",
        "Troubleshooting",
        "Agile",
        "Scrum",
    }

    REQUIRED_MARKERS = (
        "required",
        "must have",
        "must-have",
        "must possess",
        "essential",
        "mandatory",
        "need",
        "needs",
        "needed",
        "strong experience",
        "proficiency",
        "proficient",
        "expertise",
        "hands-on experience",
        "experience with",
        "experience in",
        "working experience",
        "minimum",
    )

    PREFERRED_MARKERS = (
        "preferred",
        "nice to have",
        "nice-to-have",
        "bonus",
        "plus",
        "good to have",
        "good-to-have",
        "desirable",
        "familiarity",
        "exposure",
        "knowledge of",
        "would be a plus",
        "would be nice",
    )
    
    def analyze_job(
        self,
        title: str,
        company: str,
        job_text: str,
        developer_profile: dict[str, Any] | None = None,
        repositories: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Backward-compatible API used by the existing career route
        and legacy analyzer tests.
        """

        profile = developer_profile or {}
        repos = repositories or []

        result = self.analyze(
            job_text=job_text,
            developer_profile=profile,
            repositories=repos,
            title=title,
            company=company,
        )

        # ---------------------------------------------------------
        # Legacy match_score
        # ---------------------------------------------------------
        matched_scores = [
            float(item.get("developer_score") or 0)
            for item in result.get("skill_results", [])
            if float(item.get("developer_score") or 0) > 0
        ]

        if matched_scores:
            legacy_match = sum(matched_scores) / len(matched_scores)
        else:
            legacy_match = 0.0

        result["match_score"] = round(legacy_match, 1)

        # ---------------------------------------------------------
        # Legacy skill_gaps structure
        # ---------------------------------------------------------
        strong = []
        weak = []
        missing = []

        for item in result.get("skill_results", []):
            skill = item.get("skill")
            score = float(item.get("developer_score") or 0)

            if not skill:
                continue

            if score >= 70:
                strong.append(skill)
            elif score >= 45:
                weak.append(skill)
            else:
                missing.append(skill)

        result["skill_gaps"] = {
            "strong": strong,
            "weak": weak,
            "missing": missing,
        }

        return result

    def analyze(
        self,
        job_text: str,
        developer_profile: dict[str, Any] | None = None,
        repositories: list[dict[str, Any]] | None = None,
        title: str | None = None,
        company: str | None = None,
    ) -> dict[str, Any]:

        text = self._normalize(job_text)

        if not text:
            return self._empty_result(
                title=title,
                company=company,
            )

        required_skills, preferred_skills = (
            self._extract_skill_requirements(text)
        )

        evidence = self._build_developer_evidence(
            developer_profile or {},
            repositories or [],
        )

        skill_results = []

        for skill in required_skills:
            score = self._evidence_score(
                skill,
                evidence,
            )

            skill_results.append(
                {
                    "skill": skill,
                    "importance": "required",
                    "developer_score": score,
                    "matched": score >= 45,
                    "evidence": self._evidence_for_skill(
                        skill,
                        evidence,
                    ),
                }
            )

        for skill in preferred_skills:
            score = self._evidence_score(
                skill,
                evidence,
            )

            skill_results.append(
                {
                    "skill": skill,
                    "importance": "preferred",
                    "developer_score": score,
                    "matched": score >= 45,
                    "evidence": self._evidence_for_skill(
                        skill,
                        evidence,
                    ),
                }
            )

        required_scores = [
            item["developer_score"]
            for item in skill_results
            if item["importance"] == "required"
        ]

        preferred_scores = [
            item["developer_score"]
            for item in skill_results
            if item["importance"] == "preferred"
        ]

        tech_score = self._weighted_average(
            required_scores,
            preferred_scores,
        )

        project_score = self._project_score(
            repositories or [],
            required_skills,
        )

        experience_score = self._experience_score(
            developer_profile or {},
        )

        devops_score = self._devops_score(
            required_skills,
            preferred_skills,
            evidence,
        )

        problem_solving_score = self._problem_solving_score(
            developer_profile or {},
            repositories or [],
            text,
        )

        overall_score = round(
            (
                tech_score * 0.50
                + project_score * 0.18
                + experience_score * 0.12
                + devops_score * 0.10
                + problem_solving_score * 0.10
            ),
            1,
        )

        missing_required = [
            skill
            for skill in required_skills
            if self._evidence_score(skill, evidence) < 45
        ]

        weak_required = [
            skill
            for skill in required_skills
            if 45 <= self._evidence_score(skill, evidence) < 70
        ]

        missing_preferred = [
            skill
            for skill in preferred_skills
            if self._evidence_score(skill, evidence) < 45
        ]

        feedback = self._build_feedback(
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            missing_required=missing_required,
            weak_required=weak_required,
            missing_preferred=missing_preferred,
            evidence=evidence,
            repositories=repositories or [],
        )

        return {
            "title": title or "Target Role",
            "company": company or "Target Company",
            "overall_match_score": overall_score,
            "tech_score": tech_score,
            "project_score": project_score,
            "experience_score": experience_score,
            "devops_score": devops_score,
            "problem_solving_score": problem_solving_score,
            "required_skills": required_skills,
            "preferred_skills": preferred_skills,
            "missing_skills": missing_required,
            "weak_skills": weak_required,
            "missing_preferred_skills": missing_preferred,
            "skill_results": skill_results,
            "feedback_notes": feedback,
            "matched_required_count": len(required_skills)
            - len(missing_required),
            "required_skill_count": len(required_skills),
            "matched_preferred_count": len(preferred_skills)
            - len(missing_preferred),
            "preferred_skill_count": len(preferred_skills),
        }

    def _extract_skill_requirements(
        self,
        text: str,
    ) -> tuple[list[str], list[str]]:

        required: list[str] = []
        preferred: list[str] = []

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        for skill, aliases in self.SKILL_ALIASES.items():
            positions = []

            for alias in aliases:
                if skill == "C" and alias.lower() == "c":
                    # Do not interpret the C inside C++ / C# as the C language.
                    pattern = r"(?<![a-z0-9+#])c(?![a-z0-9+#])"
                else:
                    pattern = (
                        r"(?<![a-z0-9])"
                        + re.escape(alias)
                        + r"(?![a-z0-9])"
                    )

                match = re.search(
                    pattern,
                    text,
                    flags=re.IGNORECASE,
                )

                if match:
                    positions.append(match.start())

            if not positions:
                continue

            position = min(positions)

            context_start = max(
                0,
                position - 180,
            )

            context_end = min(
                len(text),
                position + 180,
            )

            context = text[
                context_start:context_end
            ]

            classification = self._classify_context(
                context
            )

            if classification == "required":
                required.append(skill)

            elif classification == "preferred":
                preferred.append(skill)

            else:
                if self._appears_in_required_section(
                    lines,
                    skill,
                ):
                    required.append(skill)
                elif self._appears_in_preferred_section(
                    lines,
                    skill,
                ):
                    preferred.append(skill)
                else:
                    required.append(skill)

        required = self._unique_preserve_order(
            required
        )

        preferred = self._unique_preserve_order(
            preferred
        )

        preferred = [
            skill
            for skill in preferred
            if skill not in required
        ]

        return required, preferred

    def _classify_context(
        self,
        context: str,
    ) -> str | None:

        normalized = self._normalize(context)

        preferred_hits = sum(
            1
            for marker in self.PREFERRED_MARKERS
            if marker in normalized
        )

        required_hits = sum(
            1
            for marker in self.REQUIRED_MARKERS
            if marker in normalized
        )

        if preferred_hits > required_hits:
            return "preferred"

        if required_hits > preferred_hits:
            return "required"

        return None

    def _appears_in_required_section(
        self,
        lines: list[str],
        skill: str,
    ) -> bool:

        skill_aliases = self.SKILL_ALIASES.get(
            skill,
            (),
        )

        required_mode = False

        for line in lines:
            normalized = self._normalize(line)

            if any(
                marker in normalized
                for marker in self.REQUIRED_MARKERS
            ):
                required_mode = True

            if any(
                marker in normalized
                for marker in self.PREFERRED_MARKERS
            ):
                required_mode = False

            if required_mode and self._contains_alias(
                normalized,
                skill_aliases,
            ):
                return True

        return False

    def _appears_in_preferred_section(
        self,
        lines: list[str],
        skill: str,
    ) -> bool:

        skill_aliases = self.SKILL_ALIASES.get(
            skill,
            (),
        )

        preferred_mode = False

        for line in lines:
            normalized = self._normalize(line)

            if any(
                marker in normalized
                for marker in self.PREFERRED_MARKERS
            ):
                preferred_mode = True

            if any(
                marker in normalized
                for marker in self.REQUIRED_MARKERS
            ):
                preferred_mode = False

            if preferred_mode and self._contains_alias(
                normalized,
                skill_aliases,
            ):
                return True

        return False

    def _build_developer_evidence(
        self,
        profile: dict[str, Any],
        repositories: list[dict[str, Any]],
    ) -> dict[str, Any]:

        skill_scores = profile.get(
            "skill_scores"
        ) or {}

        evidence: dict[str, Any] = {
            "skills": {},
            "repositories": [],
            "portfolio_score": float(
                profile.get("portfolio_score") or 0
            ),
            "github_score": float(
                profile.get("github_score") or 0
            ),
            "readiness_score": float(
                profile.get("readiness_score") or 0
            ),
            "level": profile.get(
                "current_level"
            ),
        }

        for skill, score in skill_scores.items():
            if str(skill).startswith("_"):
                continue

            try:
                evidence["skills"][skill] = float(
                    score or 0
                )
            except (
                TypeError,
                ValueError,
            ):
                continue

        for repo in repositories:
            analysis = repo.get(
                "analysis"
            ) or {}

            tech_stack = repo.get(
                "tech_stack"
            ) or analysis.get(
                "tech_stack"
            ) or []

            if isinstance(tech_stack, dict):
                tech_stack = list(
                    tech_stack.keys()
                )

            if not isinstance(
                tech_stack,
                list,
            ):
                tech_stack = []

            # GitHub's primary repository language is first-class evidence.
            # Repo analysis may not repeat it in tech_stack, so include it
            # explicitly when comparing a JD skill against repository evidence.
            primary_language = repo.get("language")
            if primary_language and primary_language not in tech_stack:
                tech_stack.append(primary_language)

            repo_evidence = {
                "name": repo.get("name"),
                "quality_score": float(
                    repo.get(
                        "quality_score",
                        analysis.get(
                            "overall_score",
                            0,
                        ),
                    )
                    or 0
                ),
                "language": repo.get(
                    "language"
                ),
                "tech_stack": [
                    str(item)
                    for item in tech_stack
                ],
                "testing_score": self._nested_score(
                    analysis,
                    "testing",
                ),
                "devops_score": self._nested_score(
                    analysis,
                    "devops",
                ),
                "architecture_score": self._nested_score(
                    analysis,
                    "architecture",
                ),
                "code_quality_score": self._nested_score(
                    analysis,
                    "code_quality",
                ),
            }

            evidence["repositories"].append(
                repo_evidence
            )

        return evidence

    def _evidence_score(
        self,
        skill: str,
        evidence: dict[str, Any],
    ) -> float:

        direct = float(
            evidence["skills"].get(
                skill,
                0,
            )
            or 0
        )

        repo_scores = []

        for repo in evidence["repositories"]:
            tech_stack = {
                str(item).lower()
                for item in repo.get(
                    "tech_stack",
                    [],
                )
            }

            aliases = {
                alias.lower()
                for alias in self.SKILL_ALIASES.get(
                    skill,
                    (),
                )
            }

            if tech_stack & aliases:
                repo_scores.append(
                    max(
                        float(
                            repo.get(
                                "quality_score",
                                0,
                            )
                            or 0
                        ),
                        45,
                    )
                )

            if skill == "Testing":
                repo_scores.append(
                    float(
                        repo.get(
                            "testing_score",
                            0,
                        )
                        or 0
                    )
                )

            if skill in self.DEVOPS_SKILLS:
                repo_scores.append(
                    float(
                        repo.get(
                            "devops_score",
                            0,
                        )
                        or 0
                    )
                )

        if not repo_scores:
            return round(
                min(100, direct),
                1,
            )

        repo_evidence = max(repo_scores)

        if direct > 0:
            return round(
                min(
                    100,
                    direct * 0.65
                    + repo_evidence * 0.35,
                ),
                1,
            )

        return round(
            min(100, repo_evidence),
            1,
        )

    def _evidence_for_skill(
        self,
        skill: str,
        evidence: dict[str, Any],
    ) -> list[str]:

        result = []

        direct_score = float(
            evidence["skills"].get(
                skill,
                0,
            )
            or 0
        )

        if direct_score >= 70:
            result.append(
                f"Strong profile evidence ({round(direct_score)}/100)."
            )
        elif direct_score >= 45:
            result.append(
                f"Moderate profile evidence ({round(direct_score)}/100)."
            )

        for repo in evidence["repositories"]:
            tech_stack = [
                str(item).lower()
                for item in repo.get(
                    "tech_stack",
                    [],
                )
            ]

            aliases = [
                alias.lower()
                for alias in self.SKILL_ALIASES.get(
                    skill,
                    (),
                )
            ]

            if any(
                alias in tech_stack
                for alias in aliases
            ):
                result.append(
                    f"{repo.get('name')} contains {skill} evidence."
                )

        if skill == "Testing":
            strong = [
                repo.get("name")
                for repo in evidence["repositories"]
                if float(
                    repo.get(
                        "testing_score",
                        0,
                    )
                    or 0
                ) >= 60
            ]

            for repo_name in strong[:2]:
                result.append(
                    f"{repo_name} has meaningful testing evidence."
                )

        return result[:3]

    def _weighted_average(
        self,
        required_scores: list[float],
        preferred_scores: list[float],
    ) -> float:

        if not required_scores and not preferred_scores:
            return 0.0

        weighted_total = (
            sum(required_scores) * 1.0
            + sum(preferred_scores) * 0.45
        )

        weight = (
            len(required_scores)
            + len(preferred_scores) * 0.45
        )

        if weight == 0:
            return 0.0

        return round(
            weighted_total / weight,
            1,
        )

    def _project_score(
        self,
        repositories: list[dict[str, Any]],
        required_skills: list[str],
    ) -> float:

        if not repositories:
            return 0.0

        quality_scores = [
            float(
                repo.get(
                    "quality_score",
                    0,
                )
                or 0
            )
            for repo in repositories
        ]

        quality_scores.sort(
            reverse=True
        )

        top_projects = quality_scores[:5]

        quality_score = sum(
            top_projects
        ) / len(top_projects)

        if not required_skills:
            return round(
                min(100, quality_score),
                1,
            )

        matching_projects = 0

        for repo in repositories:
            analysis = repo.get(
                "analysis"
            ) or {}

            tech_stack = repo.get(
                "tech_stack"
            ) or analysis.get(
                "tech_stack"
            ) or []

            if isinstance(
                tech_stack,
                dict,
            ):
                tech_stack = list(
                    tech_stack.keys()
                )

            normalized_stack = {
                str(item).lower()
                for item in tech_stack
            }

            if any(
                any(
                    alias.lower()
                    in normalized_stack
                    for alias in self.SKILL_ALIASES.get(
                        skill,
                        (),
                    )
                )
                for skill in required_skills
            ):
                matching_projects += 1

        project_relevance = min(
            100,
            matching_projects
            / max(1, min(len(required_skills), 5))
            * 100,
        )

        return round(
            quality_score * 0.65
            + project_relevance * 0.35,
            1,
        )

    def _experience_score(
        self,
        profile: dict[str, Any],
    ) -> float:

        level = str(
            profile.get(
                "current_level",
                "",
            )
        ).lower()

        readiness = float(
            profile.get(
                "readiness_score",
                0,
            )
            or 0
        )

        level_score = {
            "advanced": 90,
            "senior": 95,
            "intermediate": 70,
            "developing": 50,
            "beginner": 35,
        }.get(
            level,
            55,
        )

        return round(
            level_score * 0.55
            + readiness * 0.45,
            1,
        )

    def _devops_score(
        self,
        required_skills: list[str],
        preferred_skills: list[str],
        evidence: dict[str, Any],
    ) -> float:

        requested = [
            skill
            for skill in (
                required_skills
                + preferred_skills
            )
            if skill in self.DEVOPS_SKILLS
        ]

        if not requested:
            return 75.0

        scores = [
            self._evidence_score(
                skill,
                evidence,
            )
            for skill in requested
        ]

        return round(
            sum(scores) / len(scores),
            1,
        )

    def _problem_solving_score(
        self,
        profile: dict[str, Any],
        repositories: list[dict[str, Any]],
        job_text: str,
    ) -> float:

        base = float(
            profile.get(
                "github_score",
                0,
            )
            or 0
        )

        quality_scores = [
            float(
                repo.get(
                    "quality_score",
                    0,
                )
                or 0
            )
            for repo in repositories
        ]

        if quality_scores:
            project_quality = sum(
                sorted(
                    quality_scores,
                    reverse=True,
                )[:5]
            ) / min(
                len(quality_scores),
                5,
            )
        else:
            project_quality = 0

        complexity_terms = (
            "architecture",
            "scalability",
            "distributed",
            "api",
            "system design",
            "optimization",
            "performance",
            "algorithms",
        )

        complexity_bonus = min(
            15,
            sum(
                2
                for term in complexity_terms
                if term in job_text
            ),
        )

        return round(
            min(
                100,
                base * 0.40
                + project_quality * 0.45
                + complexity_bonus,
            ),
            1,
        )

    def _build_feedback(
        self,
        required_skills: list[str],
        preferred_skills: list[str],
        missing_required: list[str],
        weak_required: list[str],
        missing_preferred: list[str],
        evidence: dict[str, Any],
        repositories: list[dict[str, Any]],
    ) -> list[str]:

        feedback = []

        if missing_required:
            feedback.append(
                "Missing required evidence: "
                + ", ".join(missing_required[:6])
                + "."
            )

        if weak_required:
            feedback.append(
                "Improve evidence for: "
                + ", ".join(weak_required[:5])
                + "."
            )

        if missing_preferred:
            feedback.append(
                "Preferred but currently weak or missing: "
                + ", ".join(missing_preferred[:5])
                + "."
            )

        if repositories:
            strongest = sorted(
                repositories,
                key=lambda repo: float(
                    repo.get(
                        "quality_score",
                        0,
                    )
                    or 0
                ),
                reverse=True,
            )[:2]

            names = [
                repo.get("name")
                for repo in strongest
                if repo.get("name")
            ]

            if names:
                feedback.append(
                    "Use "
                    + " and ".join(names)
                    + " as your strongest project evidence."
                )

        if not required_skills:
            feedback.append(
                "The job description did not clearly identify "
                "required technical skills; match confidence is lower."
            )

        return feedback[:6]

    def _nested_score(
        self,
        analysis: dict[str, Any],
        key: str,
    ) -> float:

        value = analysis.get(
            key
        )

        if isinstance(
            value,
            dict,
        ):
            value = value.get(
                "score",
                0,
            )

        try:
            return float(
                value or 0
            )
        except (
            TypeError,
            ValueError,
        ):
            return 0.0

    @staticmethod
    def _contains_alias(
        text: str,
        aliases: tuple[str, ...],
    ) -> bool:

        return any(
            re.search(
                r"(?<![a-z0-9])"
                + re.escape(alias)
                + r"(?![a-z0-9])",
                text,
                flags=re.IGNORECASE,
            )
            for alias in aliases
        )

    @staticmethod
    def _normalize(text: str) -> str:
        return re.sub(
            r"\s+",
            " ",
            (text or "").lower(),
        ).strip()

    @staticmethod
    def _unique_preserve_order(
        values: list[str],
    ) -> list[str]:

        seen = set()
        result = []

        for value in values:
            if value not in seen:
                seen.add(value)
                result.append(value)

        return result

    @staticmethod
    def _empty_result(
        title: str | None,
        company: str | None,
    ) -> dict[str, Any]:

        return {
            "title": title or "Target Role",
            "company": company or "Target Company",
            "overall_match_score": 0,
            "tech_score": 0,
            "project_score": 0,
            "experience_score": 0,
            "devops_score": 0,
            "problem_solving_score": 0,
            "required_skills": [],
            "preferred_skills": [],
            "missing_skills": [],
            "weak_skills": [],
            "missing_preferred_skills": [],
            "skill_results": [],
            "feedback_notes": [
                "Paste a job description to calculate a match."
            ],
            "matched_required_count": 0,
            "required_skill_count": 0,
            "matched_preferred_count": 0,
            "preferred_skill_count": 0,
        }