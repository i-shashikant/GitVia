from __future__ import annotations

import asyncio
import base64
import logging
from typing import Any

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


class GitHubAPIError(Exception):
    """Raised when GitHub API communication fails."""


class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.settings = get_settings()

        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "GitVia-Career-Intelligence",
        }

        self.timeout = httpx.Timeout(
            connect=10.0,
            read=30.0,
            write=10.0,
            pool=10.0,
        )

    async def _request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        retries = 1

        for attempt in range(retries + 1):
            try:
                async with httpx.AsyncClient(
                    timeout=self.timeout,
                    follow_redirects=True,
                ) as client:
                    response = await client.request(
                        method,
                        url,
                        headers=self.headers,
                        **kwargs,
                    )
            except httpx.ConnectTimeout as exc:
                raise GitHubAPIError(f"Connection to GitHub timed out: {url}") from exc
            except httpx.ReadTimeout as exc:
                raise GitHubAPIError(f"GitHub response timed out: {url}") from exc
            except httpx.RequestError as exc:
                raise GitHubAPIError(f"GitHub request failed: {exc}") from exc

            if response.status_code == 403 and attempt < retries:
                retry_after = response.headers.get("Retry-After")
                remaining = response.headers.get("X-RateLimit-Remaining")
                if retry_after or remaining == "0":
                    wait_s = int(retry_after or "2")
                    logger.warning("GitHub rate limited; retrying in %ss", wait_s)
                    await asyncio.sleep(min(wait_s, 10))
                    continue

            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    message = error_data.get("message", response.text)
                except Exception:
                    message = response.text

                raise GitHubAPIError(
                    f"GitHub API returned {response.status_code}: {message}"
                )

            return response

        raise GitHubAPIError(f"GitHub request failed: {url}")

    async def get_user(self) -> dict[str, Any]:
        response = await self._request("GET", f"{self.BASE_URL}/user")
        return response.json()

    async def get_user_repos(self, per_page: int = 100) -> list[dict[str, Any]]:
        repos: list[dict[str, Any]] = []
        page = 1

        while True:
            response = await self._request(
                "GET",
                f"{self.BASE_URL}/user/repos",
                params={
                    "per_page": per_page,
                    "page": page,
                    "sort": "updated",
                    "direction": "desc",
                    "affiliation": "owner",
                },
            )

            page_repos = response.json()
            if not page_repos:
                break

            repos.extend(page_repos)

            if len(page_repos) < per_page:
                break

            page += 1

        filtered = []
        for repo in repos:
            if self.settings.skip_forks and repo.get("fork"):
                continue
            if self.settings.skip_archived and repo.get("archived"):
                continue
            filtered.append(repo)

        return filtered

    async def get_repo_readme(self, owner: str, repo: str) -> str | None:
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/readme"

        try:
            response = await self._request("GET", url)
        except GitHubAPIError as exc:
            if "returned 404" in str(exc):
                return None
            raise

        data = response.json()
        content = data.get("content")
        if not content:
            return None

        try:
            return base64.b64decode(content).decode("utf-8", errors="replace")
        except Exception:
            return None

    async def get_repo_tree(
        self,
        owner: str,
        repo: str,
        branch: str = "main",
    ) -> list[str]:
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/git/trees/{branch}"

        try:
            response = await self._request(
                "GET",
                url,
                params={"recursive": "1"},
            )
        except GitHubAPIError as exc:
            if "returned 404" in str(exc):
                return []
            raise

        data = response.json()
        tree = data.get("tree", [])
        paths = [item.get("path") for item in tree if item.get("path")]
        return paths[: self.settings.max_tree_paths]
    

        async def get_repo_file(
            self,
            owner: str,
            repo: str,
            path: str,
            ref: str | None = None,
        ) -> str | None:
            """
            Fetch a single repository file from GitHub.

            We intentionally sample selected files instead of downloading
            the entire repository.
            """
            url = f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{path}"

            params = {}
            if ref:
                params["ref"] = ref

            try:
                response = await self._request(
                    "GET",
                    url,
                    params=params,
                )
            except GitHubAPIError as exc:
                if "returned 404" in str(exc):
                    return None
                raise

            data = response.json()

            # GitHub returns a list when the path points to a directory.
            if isinstance(data, list):
                return None

            content = data.get("content")
            if not content:
                return None

            try:
                return base64.b64decode(content).decode(
                    "utf-8",
                    errors="replace",
                )
            except Exception:
                return None
