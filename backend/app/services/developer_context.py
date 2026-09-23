from typing import Any

from app.github.client import GitHubClient, GitHubAPIError
from app.analyzers.repo_analyzer import RepositoryAnalyzer
from app.analyzers.profile_analyzer import ProfileAnalyzer
from app.models import User


async def build_developer_context(current_user: User) -> dict[str, Any]:
    """
    Single source of truth for "give me this user's real GitHub repos,
    their per-repo analysis, and their aggregated developer profile."

    Used by roadmap, chat, and career/job-matching endpoints so they
    don't each re-implement the fetch-and-analyze pipeline.
    """
    if not current_user.access_token:
        raise GitHubAPIError("GitHub account is not connected")

    client = GitHubClient(current_user.access_token)
    repo_analyzer = RepositoryAnalyzer()
    profile_analyzer = ProfileAnalyzer()

    repos = await client.get_user_repos()

    analyses: list[dict[str, Any]] = []
    for repo in repos:
        owner = repo["owner"]["login"]
        name = repo["name"]
        branch = repo.get("default_branch") or "main"

        try:
            readme = await client.get_repo_readme(owner, name)
        except GitHubAPIError:
            readme = None

        try:
            paths = await client.get_repo_tree(owner, name, branch)
        except GitHubAPIError:
            paths = []

        analysis = repo_analyzer.analyze_repo(
            name=name,
            readme=readme,
            paths=paths,
            language=repo.get("language"),
            stars=repo.get("stargazers_count", 0),
            forks=repo.get("forks_count", 0),
        )
        analyses.append(analysis)

    dev_profile = profile_analyzer.analyze_profile(repos, analyses)

    return {
        "repos": repos,
        "analyses": analyses,
        "profile": dev_profile,
    }