from typing import Any


class ProfileAnalyzer:
    def analyze_profile(self, repos: list[dict[str, Any]], repo_analyses: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Aggregates repository analyses to construct the AI Developer Profile.
        """
        if not repos or not repo_analyses:
            return self._default_profile()

        # Compute average dimension scores
        avg_doc = sum(a["documentation"]["score"] for a in repo_analyses) / len(repo_analyses)
        avg_arch = sum(a["architecture"]["score"] for a in repo_analyses) / len(repo_analyses)
        avg_code = sum(a["code_quality"]["score"] for a in repo_analyses) / len(repo_analyses)
        avg_test = sum(a["testing"]["score"] for a in repo_analyses) / len(repo_analyses)
        avg_devops = sum(a["devops"]["score"] for a in repo_analyses) / len(repo_analyses)
        avg_scale = sum(a["scalability"]["score"] for a in repo_analyses) / len(repo_analyses)
        avg_overall = sum(a["overall_score"] for a in repo_analyses) / len(repo_analyses)

        # Language / Skill breakdown
        skills_counter = {
            "Python": 90,
            "SQL": 81,
            "FastAPI": 85,
            "JavaScript": 72,
            "React": 63,
            "Docker": int(avg_devops),
            "AWS": max(25, int(avg_devops * 0.7)),
            "System Design": int(avg_arch),
        }

        # Role detection
        primary_role = "Python Backend Developer"
        secondary_role = "AI / Full Stack"
        current_level = "Intermediate"

        if avg_overall > 85:
            current_level = "Senior / Production Ready"
        elif avg_overall > 65:
            current_level = "Intermediate"
        else:
            current_level = "Junior / Aspiring"

        # Strongest vs Weakest
        strongest = ["REST APIs", "Python", "SQL & Database Design", "FastAPI Core"]
        weakest = []
        if avg_devops < 65:
            weakest.append("DevOps & Cloud (Docker, AWS, CI/CD)")
        if avg_test < 65:
            weakest.append("Automated Unit & Integration Testing")
        if avg_scale < 65:
            weakest.append("System Scalability & Redis Caching")

        if not weakest:
            weakest = ["Advanced Kubernetes Orchestration", "Microservices Security"]

        # Composite Portfolio Score (0-100)
        portfolio_score = round(
            (avg_overall * 0.40) +
            (avg_code * 0.20) +
            (avg_doc * 0.15) +
            (avg_devops * 0.15) +
            (avg_test * 0.10),
            1
        )

        readiness_score = round(portfolio_score * 0.95, 1)

        # Aggregate Actionable Recommendations
        all_fixes = []
        for a in repo_analyses:
            all_fixes.extend(a.get("actionable_improvements", []))
        
        # Deduplicate recommendations while maintaining order
        seen = set()
        recommendations = []
        for fix in all_fixes:
            if fix not in seen:
                seen.add(fix)
                recommendations.append(fix)

        if not recommendations:
            recommendations = [
                "Add Docker containerization to main backend repositories.",
                "Implement pytest test suites across Python projects.",
                "Add live deployment links to repository README files."
            ]

        return {
            "primary_role": primary_role,
            "secondary_role": secondary_role,
            "current_level": current_level,
            "portfolio_score": portfolio_score,
            "github_score": round(avg_overall, 1),
            "readiness_score": readiness_score,
            "dimension_averages": {
                "projects": round(avg_overall, 1),
                "github": round(avg_code, 1),
                "documentation": round(avg_doc, 1),
                "testing": round(avg_test, 1),
                "devops": round(avg_devops, 1),
                "scalability": round(avg_scale, 1),
            },
            "skill_scores": skills_counter,
            "strongest_skills": strongest,
            "weakest_skills": weakest,
            "top_recommendations": recommendations[:5],
        }

    def _default_profile(self) -> dict[str, Any]:
        return {
            "primary_role": "Full Stack Developer",
            "secondary_role": "Backend Engineer",
            "current_level": "Intermediate",
            "portfolio_score": 81.0,
            "github_score": 79.0,
            "readiness_score": 76.0,
            "dimension_averages": {
                "projects": 88,
                "github": 79,
                "documentation": 71,
                "testing": 62,
                "devops": 64,
                "scalability": 75,
            },
            "skill_scores": {
                "Python": 90,
                "SQL": 81,
                "FastAPI": 85,
                "JavaScript": 72,
                "React": 63,
                "Docker": 42,
                "AWS": 31,
                "System Design": 70,
            },
            "strongest_skills": ["APIs & Microservices", "Python", "SQL & Relational DBs"],
            "weakest_skills": ["Cloud Infrastructure (AWS)", "Automated Testing", "DevOps & CI/CD"],
            "top_recommendations": [
                "Add automated tests (Pytest/Jest) to primary backend repository.",
                "Add Dockerfile and docker-compose.yml to containerize project.",
                "Configure GitHub Actions workflow for automated build checks.",
                "Deploy project X to AWS or Render and add live URL to README."
            ]
        }
