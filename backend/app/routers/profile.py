from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.session import get_current_user
from app.database import get_db
from app.github.client import GitHubAPIError, GitHubClient
from app.models import User
from app.analyzers.repo_analyzer import RepositoryAnalyzer

router = APIRouter(
    prefix="/api/profile",
    tags=["Developer Profile"],
)


@router.get("")
async def get_developer_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Build the developer profile from the user's REAL GitHub repositories.

    Nothing is hardcoded here.
    """

    if not current_user.access_token:
        raise HTTPException(
            status_code=401,
            detail="GitHub account is not connected",
        )

    # ------------------------------------------------------------
    # GitHub client
    # ------------------------------------------------------------

    client = GitHubClient(
        current_user.access_token
    )

    analyzer = RepositoryAnalyzer()

    try:
        # Get REAL GitHub repositories
        github_repos = await client.get_user_repos()

    except GitHubAPIError as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc),
        )

    # ------------------------------------------------------------
    # Analyze repositories
    # ------------------------------------------------------------

    analyses = []

    for repo in github_repos:

        owner = repo["owner"]["login"]
        name = repo["name"]

        branch = (
            repo.get("default_branch")
            or "main"
        )

        # README
        try:

            readme = await client.get_repo_readme(
                owner,
                name,
            )

        except GitHubAPIError:

            readme = None

        # Repository tree
        try:

            paths = await client.get_repo_tree(
                owner,
                name,
                branch,
            )

        except GitHubAPIError:

            paths = []

        # Analyze repository
        analysis = analyzer.analyze_repo(
            name=name,
            readme=readme,
            paths=paths,
            language=repo.get("language"),
            stars=repo.get(
                "stargazers_count",
                0,
            ),
            forks=repo.get(
                "forks_count",
                0,
            ),
        )

        analyses.append(
            {
                "repo": repo,
                "analysis": analysis,
            }
        )

    # ------------------------------------------------------------
    # No repositories
    # ------------------------------------------------------------

    if not analyses:

        return {
            "user": {
                "id": current_user.id,
                "github_id": current_user.github_id,
                "github_username": current_user.github_username,
                "name": current_user.name,
                "email": current_user.email,
                "avatar_url": current_user.avatar_url,
            },
            "repository_count": 0,
            "profile": {
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
                },
                "skill_scores": {},
                "strongest_skills": [],
                "weakest_skills": [],
                "top_recommendations": [],
            },
        }

    # ------------------------------------------------------------
    # Aggregate repository scores
    # ------------------------------------------------------------

    repo_count = len(analyses)

    documentation_scores = [
        item["analysis"]["documentation"]["score"]
        for item in analyses
    ]

    architecture_scores = [
        item["analysis"]["architecture"]["score"]
        for item in analyses
    ]

    code_scores = [
        item["analysis"]["code_quality"]["score"]
        for item in analyses
    ]

    testing_scores = [
        item["analysis"]["testing"]["score"]
        for item in analyses
    ]

    devops_scores = [
        item["analysis"]["devops"]["score"]
        for item in analyses
    ]

    scalability_scores = [
        item["analysis"]["scalability"]["score"]
        for item in analyses
    ]

    overall_scores = [
        item["analysis"]["overall_score"]
        for item in analyses
    ]

    def average(values):
        if not values:
            return 0

        return round(
            sum(values) / len(values),
            1,
        )

    documentation_avg = average(
        documentation_scores
    )

    architecture_avg = average(
        architecture_scores
    )

    code_avg = average(
        code_scores
    )

    testing_avg = average(
        testing_scores
    )

    devops_avg = average(
        devops_scores
    )

    scalability_avg = average(
        scalability_scores
    )

    github_score = average(
        overall_scores
    )

    # ------------------------------------------------------------
    # Portfolio score
    # ------------------------------------------------------------

    portfolio_score = round(
        (
            documentation_avg * 0.20
            + architecture_avg * 0.20
            + code_avg * 0.20
            + testing_avg * 0.15
            + devops_avg * 0.15
            + scalability_avg * 0.10
        ),
        1,
    )

    # ------------------------------------------------------------
    # Readiness score
    # ------------------------------------------------------------

    readiness_score = round(
        (
            portfolio_score * 0.50
            + github_score * 0.50
        ),
        1,
    )

    # ------------------------------------------------------------
    # Aggregate recommendations
    # ------------------------------------------------------------

    recommendations = []

    for item in analyses:

        repo_name = item["repo"]["name"]

        improvements = item["analysis"].get(
            "actionable_improvements",
            [],
        )

        for improvement in improvements:

            if improvement not in recommendations:

                recommendations.append(
                    improvement
                )

    # Keep the dashboard manageable
    recommendations = recommendations[:8]

    # ------------------------------------------------------------
    # Skill estimation from actual repository languages
    # ------------------------------------------------------------

    language_counts = {}

    for item in analyses:

        language = item["repo"].get(
            "language"
        )

        if language:

            language_counts[language] = (
                language_counts.get(
                    language,
                    0,
                )
                + 1
            )

    skill_scores = {}

    for language, count in language_counts.items():

        # More repositories using a language
        # increases confidence, but is capped.
        score = min(
            95,
            50 + (count * 10),
        )

        skill_scores[language] = score

    # ------------------------------------------------------------
    # Determine strongest / weakest dimensions
    # ------------------------------------------------------------

    dimension_scores = {
        "Documentation": documentation_avg,
        "Architecture": architecture_avg,
        "Code Quality": code_avg,
        "Testing": testing_avg,
        "DevOps": devops_avg,
        "Scalability": scalability_avg,
    }

    sorted_dimensions = sorted(
        dimension_scores.items(),
        key=lambda x: x[1],
        reverse=True,
    )

    strongest_skills = [
        item[0]
        for item in sorted_dimensions[:3]
    ]

    weakest_skills = [
        item[0]
        for item in sorted_dimensions[-3:]
    ]

    # ------------------------------------------------------------
    # Role estimation
    # ------------------------------------------------------------

    languages = {
        language.lower()
        for language in language_counts
    }

    if "python" in languages:

        primary_role = "Python Developer"

    elif "typescript" in languages:

        primary_role = "TypeScript Developer"

    elif "javascript" in languages:

        primary_role = "JavaScript Developer"

    else:

        primary_role = "Software Developer"

    if (
        "typescript" in languages
        or "javascript" in languages
    ):

        secondary_role = "Full Stack Developer"

    else:

        secondary_role = "Software / Backend"

    # ------------------------------------------------------------
    # Level
    # ------------------------------------------------------------

    if readiness_score >= 75:

        current_level = "Intermediate"

    elif readiness_score >= 50:

        current_level = "Junior"

    else:

        current_level = "Aspiring / Junior"

    # ------------------------------------------------------------
    # Final response
    # ------------------------------------------------------------

    return {
        "user": {
            "id": current_user.id,
            "github_id": current_user.github_id,
            "github_username": current_user.github_username,
            "name": current_user.name,
            "email": current_user.email,
            "avatar_url": current_user.avatar_url,
        },

        "repository_count": repo_count,

        "profile": {
            "primary_role": primary_role,
            "secondary_role": secondary_role,
            "current_level": current_level,

            "portfolio_score": portfolio_score,

            "github_score": github_score,

            "readiness_score": readiness_score,

            "dimension_averages": {
                "projects": github_score,
                "github": github_score,
                "documentation": documentation_avg,
                "testing": testing_avg,
                "devops": devops_avg,
                "scalability": scalability_avg,
            },

            "skill_scores": skill_scores,

            "strongest_skills": strongest_skills,

            "weakest_skills": weakest_skills,

            "top_recommendations": recommendations,
        },
    }