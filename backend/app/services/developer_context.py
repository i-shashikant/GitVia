import asyncio
from typing import Any

from app.github.client import GitHubClient, GitHubAPIError
from app.analyzers.repo_analyzer import RepositoryAnalyzer
from app.analyzers.profile_analyzer import ProfileAnalyzer
from app.models import User


async def _analyze_single_repo(
    client: GitHubClient,
    repo: dict[str, Any],
    repo_analyzer: RepositoryAnalyzer,
) -> dict[str, Any]:

    owner = repo["owner"]["login"]
    name = repo["name"]
    branch = repo.get("default_branch") or "main"

    readme_task = client.get_repo_readme(owner, name)
    tree_task = client.get_repo_tree(owner, name, branch)

    readme, paths = await asyncio.gather(
        readme_task,
        tree_task,
        return_exceptions=True,
    )

    if isinstance(readme, Exception):
        readme = None

    if isinstance(paths, Exception):
        paths = []

    return repo_analyzer.analyze_repo(
        name=name,
        readme=readme,
        paths=paths,
        language=repo.get("language"),
        stars=repo.get("stargazers_count", 0),
        forks=repo.get("forks_count", 0),
    )


async def build_developer_context(
    current_user: User,
) -> dict[str, Any]:

    if not current_user.access_token:
        raise GitHubAPIError(
            "GitHub account is not connected"
        )

    client = GitHubClient(
        current_user.access_token
    )

    repo_analyzer = RepositoryAnalyzer()
    profile_analyzer = ProfileAnalyzer()

    # Fetch repositories once.
    repos = await client.get_user_repos()

    # Analyze repositories concurrently.
    tasks = [
        _analyze_single_repo(
            client,
            repo,
            repo_analyzer,
        )
        for repo in repos
    ]

    analyses = await asyncio.gather(
        *tasks,
        return_exceptions=True,
    )

    clean_analyses = [
        analysis
        for analysis in analyses
        if not isinstance(analysis, Exception)
    ]

    dev_profile = profile_analyzer.analyze_profile(
        repos,
        clean_analyses,
    )

    return {
        "repos": repos,
        "analyses": clean_analyses,
        "profile": dev_profile,
    }