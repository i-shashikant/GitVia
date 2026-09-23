from __future__ import annotations

import base64
from typing import Any

import httpx


class GitHubAPIError(Exception):
    """Raised when GitHub API communication fails."""

    pass


class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, access_token: str):
        self.access_token = access_token

        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "GitVia-Career-Intelligence",
        }

        # Keep connection timeout short enough that one bad request
        # does not make the entire repository analysis hang.
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
            raise GitHubAPIError(
                f"Connection to GitHub timed out: {url}"
            ) from exc

        except httpx.ReadTimeout as exc:
            raise GitHubAPIError(
                f"GitHub response timed out: {url}"
            ) from exc

        except httpx.RequestError as exc:
            raise GitHubAPIError(
                f"GitHub request failed: {exc}"
            ) from exc

        if response.status_code >= 400:
            try:
                error_data = response.json()
                message = error_data.get(
                    "message",
                    response.text,
                )
            except Exception:
                message = response.text

            raise GitHubAPIError(
                f"GitHub API returned {response.status_code}: {message}"
            )

        return response

    async def get_user(self) -> dict[str, Any]:
        response = await self._request(
            "GET",
            f"{self.BASE_URL}/user",
        )

        return response.json()

    async def get_user_repos(
        self,
        per_page: int = 100,
    ) -> list[dict[str, Any]]:

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
                },
            )

            page_repos = response.json()

            if not page_repos:
                break

            repos.extend(page_repos)

            if len(page_repos) < per_page:
                break

            page += 1

        return repos

    async def get_repo_readme(
        self,
        owner: str,
        repo: str,
    ) -> str | None:

        url = (
            f"{self.BASE_URL}/repos/"
            f"{owner}/{repo}/readme"
        )

        try:
            response = await self._request(
                "GET",
                url,
            )

        except GitHubAPIError as exc:

            # A missing README should NOT fail repository analysis.
            if "returned 404" in str(exc):
                return None

            raise

        data = response.json()

        content = data.get("content")

        if not content:
            return None

        try:
            decoded = base64.b64decode(
                content
            ).decode(
                "utf-8",
                errors="replace",
            )

            return decoded

        except Exception:
            return None

    async def get_repo_tree(
        self,
        owner: str,
        repo: str,
        branch: str = "main",
    ) -> list[str]:

        url = (
            f"{self.BASE_URL}/repos/"
            f"{owner}/{repo}/git/trees/{branch}"
        )

        response = await self._request(
            "GET",
            url,
            params={
                "recursive": "1",
            },
        )

        data = response.json()

        tree = data.get("tree", [])

        paths = []

        for item in tree:
            path = item.get("path")

            if path:
                paths.append(path)

        return paths