import re
from typing import Any


class ResumeAnalyzer:
    def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        try:
            import fitz
        except ImportError:
            fitz = None

        if fitz:
            try:
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                text = ""
                for page in doc:
                    text += page.get_text("text") + "\n"
                if text.strip():
                    return text
            except Exception:
                pass

        try:
            return pdf_bytes.decode("utf-8", errors="ignore")
        except Exception:
            return ""

    def analyze_resume(self, text: str, user_repos: list[dict[str, Any]]) -> dict[str, Any]:
        lower_text = text.lower()

        possible_skills = [
            "Python", "JavaScript", "TypeScript", "React", "Next.js", "FastAPI",
            "Django", "Flask", "PostgreSQL", "MongoDB", "Docker", "Kubernetes",
            "AWS", "Redis", "Celery", "SQL", "Git", "CI/CD", "Pytest", "Tailwind",
            "Terraform", "Java", "Go",
        ]
        extracted_skills = [
            skill for skill in possible_skills if skill.lower() in lower_text
        ]

        education_match = re.search(
            r"(b\.?tech|b\.?e\.?|m\.?tech|bachelor|master|phd).{0,80}",
            text,
            flags=re.IGNORECASE,
        )
        education = education_match.group(0).strip() if education_match else None

        experience: list[dict[str, str]] = []
        for match in re.finditer(
            r"(intern|engineer|developer|software).{0,60}",
            text,
            flags=re.IGNORECASE,
        ):
            snippet = match.group(0).strip()
            if snippet and snippet not in [item.get("role") for item in experience]:
                experience.append({"role": snippet, "company": "", "highlights": []})
            if len(experience) >= 3:
                break

        repo_evidence: set[str] = set()
        for repo in user_repos:
            if repo.get("language"):
                repo_evidence.add(str(repo["language"]).lower())
            for tech in repo.get("tech_stack") or []:
                repo_evidence.add(str(tech).lower())
            analysis = str(repo.get("analysis") or "").lower()
            repo_evidence.update(token for token in analysis.split() if len(token) > 2)

        mismatches = []
        for claim in extracted_skills:
            if claim.lower() not in repo_evidence:
                mismatches.append(
                    {
                        "type": "warning",
                        "skill": claim,
                        "message": (
                            f"Resume claims '{claim}', but analyzed GitHub repositories "
                            "do not show matching file or README evidence."
                        ),
                        "action": (
                            f"Add a public repository or README section that demonstrates {claim}."
                        ),
                    }
                )

        repo_names = [repo.get("name") for repo in user_repos if repo.get("name")]
        bullets = []
        if repo_names:
            bullets.append(
                {
                    "original": "Worked on personal projects.",
                    "improved": (
                        f"Built and published {repo_names[0]} with documented setup, "
                        "visible architecture, and GitHub-hosted source."
                    ),
                }
            )

        return {
            "parsed_skills": extracted_skills,
            "education": education,
            "experience": experience,
            "mismatch_flags": mismatches,
            "bullets_suggestions": bullets,
        }
