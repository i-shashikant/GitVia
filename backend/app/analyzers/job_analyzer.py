from typing import Any


class JobAnalyzer:
    def analyze_job(
        self,
        title: str,
        company: str,
        job_text: str,
        dev_profile: dict[str, Any],
    ) -> dict[str, Any]:
        lower_job = job_text.lower()

        all_possible = {
            "python": "Python",
            "fastapi": "FastAPI",
            "postgresql": "PostgreSQL",
            "sql": "SQL",
            "docker": "Docker",
            "aws": "AWS",
            "redis": "Redis",
            "kubernetes": "Kubernetes",
            "ci/cd": "CI/CD",
            "github actions": "CI/CD",
            "machine learning": "Machine Learning",
            "react": "React",
            "typescript": "TypeScript",
            "system design": "System Design",
            "rest api": "REST APIs",
            "pytest": "Pytest",
            "javascript": "JavaScript",
            "next.js": "Next.js",
        }

        mentioned: list[str] = []
        for key, display in all_possible.items():
            if key in lower_job and display not in mentioned:
                mentioned.append(display)

        required_skills = mentioned[:5]
        preferred_skills = mentioned[5:]

        user_skills = {
            str(key).lower(): float(value)
            for key, value in (dev_profile.get("skill_scores") or {}).items()
            if isinstance(value, (int, float))
        }
        dimensions = dev_profile.get("dimension_averages") or {}
        devops_score = float(dimensions.get("devops", 0) or 0)
        project_score = float(dimensions.get("projects", 0) or 0)

        strong_skills = []
        improving_skills = []
        missing_skills = []

        for skill in required_skills + preferred_skills:
            score = user_skills.get(skill.lower(), 0)
            if score >= 70:
                strong_skills.append(skill)
            elif score >= 35:
                improving_skills.append(skill)
            else:
                missing_skills.append(skill)

        skill_values = [
            user_skills.get(skill.lower(), 0)
            for skill in required_skills
        ]
        tech_score = round(sum(skill_values) / len(skill_values), 1) if skill_values else 0
        exp_score = min(100, round(project_score * 0.8, 1))
        prob_score = min(100, round((project_score + float(dimensions.get("code_quality", project_score))) / 2, 1))

        overall_match = round(
            (tech_score * 0.30)
            + (project_score * 0.25)
            + (exp_score * 0.15)
            + (devops_score * 0.15)
            + (prob_score * 0.15),
            1,
        )

        notes = []
        if missing_skills:
            notes.append(
                "No GitHub evidence for: " + ", ".join(missing_skills) + "."
            )
        if devops_score < 60:
            notes.append(
                "DevOps score is below 60. A Dockerfile or GitHub Actions workflow on a flagship repo would raise this match."
            )
        if not notes:
            notes.append("Required skills are supported by analyzed GitHub evidence.")

        return {
            "title": title or "Target role",
            "company": company or None,
            "match_score": overall_match,
            "score_breakdown": {
                "technical_skills": tech_score,
                "projects": project_score,
                "experience": exp_score,
                "devops": devops_score,
                "problem_solving": prob_score,
            },
            "required_skills": required_skills,
            "preferred_skills": preferred_skills,
            "skill_gaps": {
                "strong": list(dict.fromkeys(strong_skills)),
                "improving": list(dict.fromkeys(improving_skills)),
                "missing": list(dict.fromkeys(missing_skills)),
            },
            "missing_evidence_notes": notes,
        }
