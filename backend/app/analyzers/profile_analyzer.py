from typing import Any

from app.analyzers.career_analyzer import CareerAnalyzer


class ProfileAnalyzer:
    def analyze_profile(
        self,
        repos: list[dict[str, Any]],
        repo_analyses: list[dict[str, Any]],
    ) -> dict[str, Any]:
        if not repos or not repo_analyses:
            return self._default_profile()

        def average(key_path: list[str]) -> float:
            values = []
            for analysis in repo_analyses:
                node: Any = analysis
                for key in key_path:
                    node = (node or {}).get(key) if isinstance(node, dict) else None
                if isinstance(node, (int, float)):
                    values.append(float(node))
            if not values:
                return 0.0
            return round(sum(values) / len(values), 1)

        avg_doc = average(["documentation", "score"])
        avg_arch = average(["architecture", "score"])
        avg_code = average(["code_quality", "score"])
        avg_test = average(["testing", "score"])
        avg_devops = average(["devops", "score"])
        avg_scale = average(["scalability", "score"])
        avg_overall = average(["overall_score"])

        analysis_by_name = {
            analysis.get("name"): analysis
            for analysis in repo_analyses
            if analysis.get("name")
        }

        enriched = []
        for index, repo in enumerate(repos):
            name = repo.get("name")
            analysis = analysis_by_name.get(name)
            if analysis is None and index < len(repo_analyses):
                analysis = repo_analyses[index]
            analysis = analysis or {}
            enriched.append(
                {
                    **repo,
                    "analysis": analysis,
                    "quality_score": analysis.get("overall_score", 0),
                    "tech_stack": repo.get("tech_stack")
                    or analysis.get("tech_stack")
                    or [],
                }
            )

        career = CareerAnalyzer().analyze(enriched)

        recommendations = list(career.get("recommended_actions") or [])
        seen = set(recommendations)
        for analysis in repo_analyses:
            for fix in analysis.get("actionable_improvements", []):
                if fix not in seen:
                    seen.add(fix)
                    recommendations.append(fix)

        return {
            "primary_role": career.get("primary_role") or "Software Developer",
            "secondary_role": career.get("secondary_role") or "Software Developer",
            "current_level": career.get("current_level") or "Developing",
            "portfolio_score": career.get("portfolio_score") or 0,
            "github_score": career.get("github_score") or avg_overall,
            "readiness_score": career.get("readiness_score") or 0,
            "dimension_averages": {
                "projects": avg_overall,
                "github": avg_overall,
                "documentation": avg_doc,
                "testing": avg_test,
                "devops": avg_devops,
                "scalability": avg_scale,
                "architecture": avg_arch,
                "code_quality": avg_code,
            },
            "skill_scores": career.get("skill_scores") or {},
            "strongest_skills": career.get("strongest_skills") or [],
            "weakest_skills": career.get("weakest_skills") or [],
            "top_recommendations": recommendations[:8],
            "role_matches": career.get("role_matches") or [],
            "career_gaps": career.get("career_gaps") or [],
        }

    def _default_profile(self) -> dict[str, Any]:
        return {
            "primary_role": "Unknown",
            "secondary_role": "Unknown",
            "current_level": "Unknown",
            "portfolio_score": 0,
            "github_score": 0,
            "readiness_score": 0,
            "dimension_averages": {
                "projects": 0,
                "github": 0,
                "documentation": 0,
                "testing": 0,
                "devops": 0,
                "scalability": 0,
                "architecture": 0,
                "code_quality": 0,
            },
            "skill_scores": {},
            "strongest_skills": [],
            "weakest_skills": [],
            "top_recommendations": [
                "Connect GitHub and analyze at least one original repository."
            ],
            "role_matches": [],
            "career_gaps": [],
        }
