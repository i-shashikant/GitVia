from typing import Any


class CareerChatAssistant:

    def generate_response(
        self,
        user_query: str,
        dev_profile: dict[str, Any],
        repos: list[dict[str, Any]],
        analyses: list[dict[str, Any]] | None = None,
        job_context: dict[str, Any] | None = None,
        resume_context: dict[str, Any] | None = None,
    ) -> str:

        analyses = analyses or []

        query = user_query.lower().strip()

        strongest = dev_profile.get(
            "strongest_skills",
            [],
        )

        weakest = dev_profile.get(
            "weakest_skills",
            [],
        )

        portfolio_score = dev_profile.get(
            "portfolio_score",
            0,
        )

        github_score = dev_profile.get(
            "github_score",
            0,
        )

        readiness_score = dev_profile.get(
            "readiness_score",
            0,
        )

        primary_role = dev_profile.get(
            "primary_role",
            "Developer",
        )

        # When a job has been analyzed, let the assistant answer from the
        # latest real match instead of pretending the job context does not exist.
        if job_context and any(
            phrase in query
            for phrase in (
                "match",
                "job description",
                "missing skill",
                "missing skills",
                "job requirements",
                "this job",
                "that job",
            )
        ):
            return self._job_response(job_context)

        if resume_context and any(
            phrase in query
            for phrase in (
                "resume",
                "cv",
                "mismatch",
                "claim",
            )
        ):
            return self._resume_response(resume_context)

        repo_names = [
            repo.get("name")
            for repo in repos
            if repo.get("name")
        ]

        # ---------------------------------------------------------
        # READY / INTERNSHIP
        # ---------------------------------------------------------

        if (
            "ready" in query
            or "internship" in query
            or "job" in query
        ):
            return self._readiness_response(
                primary_role,
                readiness_score,
                strongest,
                weakest,
                repo_names,
            )

        # ---------------------------------------------------------
        # RESUME / PROJECTS
        # ---------------------------------------------------------

        if (
            "resume" in query
            or "project" in query
            or "portfolio" in query
        ):
            return self._project_response(
                repo_names,
                analyses,
            )

        # ---------------------------------------------------------
        # KUBERNETES
        # ---------------------------------------------------------

        if (
            "kubernetes" in query
            or "k8s" in query
        ):
            return self._kubernetes_response(
                weakest,
                strongest,
            )

        # ---------------------------------------------------------
        # SCORE
        # ---------------------------------------------------------

        if (
            "score" in query
            or "low" in query
            or "github" in query
        ):
            return self._score_response(
                github_score,
                portfolio_score,
                weakest,
                analyses,
            )

        # ---------------------------------------------------------
        # WHAT NEXT / BUILD
        # ---------------------------------------------------------

        if (
            "build" in query
            or "next" in query
            or "improve" in query
            or "learn" in query
        ):
            return self._next_step_response(
                repos,
                weakest,
                dev_profile,
            )

        # ---------------------------------------------------------
        # GENERAL
        # ---------------------------------------------------------

        return self._general_response(
            primary_role,
            portfolio_score,
            strongest,
            weakest,
            repo_names,
        )

    def _job_response(
        self,
        job: dict[str, Any],
    ) -> str:
        title = job.get("title") or "Target role"
        company = job.get("company") or "the company"
        score = job.get("overall_match_score", 0)
        missing = job.get("missing_skills") or []
        feedback = job.get("feedback_notes") or []

        response = (
            f"### Latest job match\n\n"
            f"**Role:** {title}\n"
            f"**Company:** {company}\n"
            f"**Match:** {score}%\n\n"
        )

        if missing:
            response += (
                "**Main missing requirements:** "
                + ", ".join(map(str, missing[:8]))
                + "\n\n"
            )

        if feedback:
            response += "**What GitVia found:**\n\n"
            for note in feedback[:4]:
                response += f"- {note}\n"
            response += "\n"

        response += (
            "Use the Career page's **Build Roadmap for This Job** action "
            "to turn these gaps into a job-specific execution plan."
        )

        return response

    def _resume_response(
        self,
        resume: dict[str, Any],
    ) -> str:
        flags = resume.get("mismatch_flags") or []
        filename = resume.get("filename") or "your latest resume"

        response = f"### Resume evidence check\n\n**File:** {filename}\n\n"

        if not flags:
            return response + (
                "GitVia did not record any resume ↔ GitHub mismatch flags "
                "for the latest upload. That does not prove every claim is "
                "correct; it means the analyzer found no flagged mismatch."
            )

        response += "**Flags recorded by GitVia:**\n\n"
        for flag in flags[:6]:
            if isinstance(flag, dict):
                message = flag.get("message") or flag.get("claim") or str(flag)
                action = flag.get("action")
                response += f"- {message}"
                if action:
                    response += f" — {action}"
                response += "\n"
            else:
                response += f"- {flag}\n"

        return response

    # =============================================================
    # RESPONSES
    # =============================================================

    def _readiness_response(
        self,
        role: str,
        readiness: float,
        strongest: list[Any],
        weakest: list[Any],
        repos: list[str],
    ) -> str:

        response = (
            f"### Your current profile\n\n"
            f"**Primary role:** {role}\n"
            f"**Readiness score:** {readiness}/100\n\n"
        )

        if strongest:
            response += (
                f"**Current strengths:** "
                f"{', '.join(map(str, strongest[:5]))}\n\n"
            )

        if weakest:
            response += (
                f"**Current gaps:** "
                f"{', '.join(map(str, weakest[:5]))}\n\n"
            )

        response += (
            "For your next step, focus on closing the largest "
            "evidence gaps rather than starting an unrelated project."
        )

        return response

    def _project_response(
        self,
        repos: list[str],
        analyses: list[dict[str, Any]],
    ) -> str:

        if not repos:
            return (
                "I couldn't find any GitHub repositories in the "
                "current account context."
            )

        # Use actual repository analysis when available.
        scored = []

        for index, repo in enumerate(repos):
            score = 0

            if index < len(analyses):
                score = analyses[index].get(
                    "overall_score",
                    0,
                )

            scored.append(
                (repo, score)
            )

        scored.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        response = "### Projects to consider\n\n"

        for index, (repo, score) in enumerate(
            scored[:3],
            start=1,
        ):
            response += (
                f"{index}. **{repo}**"
            )

            if score:
                response += (
                    f" — repository quality score: "
                    f"**{score}/100**"
                )

            response += "\n"

        response += (
            "\nUse the repositories with the strongest engineering "
            "evidence and the clearest README/project story on your "
            "resume."
        )

        return response

    def _kubernetes_response(
        self,
        weakest: list[Any],
        strongest: list[Any],
    ) -> str:

        weak_text = " ".join(
            str(skill).lower()
            for skill in weakest
        )

        if (
            "docker" in weak_text
            or "devops" in weak_text
            or "cloud" in weak_text
        ):
            return (
                "Before Kubernetes, strengthen the infrastructure "
                "fundamentals already identified as gaps in your "
                "profile.\n\n"
                "Focus on **Docker → Docker Compose → deployment → "
                "CI/CD**, then move into Kubernetes."
            )

        return (
            "Kubernetes can be useful for backend/cloud roles, but "
            "your current profile does not require making it the "
            "immediate priority. Build evidence around your existing "
            "stack first, then add Kubernetes when you have a "
            "deployment workflow to orchestrate."
        )

    def _score_response(
        self,
        github_score: float,
        portfolio_score: float,
        weakest: list[Any],
        analyses: list[dict[str, Any]],
    ) -> str:

        response = (
            f"### Current GitVia metrics\n\n"
            f"- **GitHub score:** {github_score}/100\n"
            f"- **Portfolio score:** {portfolio_score}/100\n\n"
        )

        if weakest:
            response += (
                "**Main areas reducing your profile strength:**\n\n"
            )

            for skill in weakest[:5]:
                response += f"- {skill}\n"

        response += (
            "\nThese are the areas I'd investigate first instead "
            "of assuming that adding another project will improve "
            "the profile."
        )

        return response

    def _next_step_response(
        self,
        repos: list[dict[str, Any]],
        weakest: list[Any],
        profile: dict[str, Any],
    ) -> str:

        repo_name = (
            repos[0].get("name")
            if repos
            else "your existing project"
        )

        if weakest:
            first_gap = str(weakest[0])

            return (
                f"### Your next move\n\n"
                f"The strongest signal in your current profile is "
                f"the gap around **{first_gap}**.\n\n"
                f"Instead of starting a new generic project, use "
                f"**{repo_name}** to create evidence for that skill.\n\n"
                f"Build one concrete feature, test it, document it, "
                f"and commit the result."
            )

        return (
            f"Your profile doesn't show a single dominant gap right "
            f"now. Use **{repo_name}** to strengthen production "
            f"evidence: testing, deployment, documentation, and "
            f"measurable performance."
        )

    def _general_response(
        self,
        role: str,
        portfolio_score: float,
        strongest: list[Any],
        weakest: list[Any],
        repos: list[str],
    ) -> str:

        return (
            f"### GitVia Career Context\n\n"
            f"**Role:** {role}\n"
            f"**Portfolio score:** {portfolio_score}/100\n"
            f"**Repositories analyzed:** {len(repos)}\n\n"
            f"**Strengths:** "
            f"{', '.join(map(str, strongest[:4])) or 'No strong skills detected'}\n\n"
            f"**Areas to improve:** "
            f"{', '.join(map(str, weakest[:4])) or 'No major gaps detected'}"
        )