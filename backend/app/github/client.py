from typing import Any

import httpx


class GitHubAPIError(Exception):
    """Raised when the GitHub API returns an unexpected response."""


class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, access_token: str):
        if not access_token:
            raise ValueError("GitHub access token is required")

        self.access_token = access_token

        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "GitVia-Career-Intelligence",
        }

    async def _get(
        self,
        url: str,
        **kwargs,
    ) -> httpx.Response:

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                url,
                headers=self.headers,
                **kwargs,
            )

        if response.status_code == 401:
            raise GitHubAPIError(
                "GitHub authentication failed. Please reconnect GitHub."
            )

        if response.status_code == 403:
            raise GitHubAPIError(
                "GitHub API access was forbidden or rate limited."
            )

        if response.status_code >= 400:
            raise GitHubAPIError(
                f"GitHub API request failed with status "
                f"{response.status_code}"
            )

        return response

    async def get_user_profile(self) -> dict[str, Any]:
        response = await self._get(
            f"{self.BASE_URL}/user"
        )

        return response.json()

    async def get_user_repos(
        self,
        per_page: int = 100,
    ) -> list[dict[str, Any]]:

        response = await self._get(
            f"{self.BASE_URL}/user/repos",
            params={
                "per_page": per_page,
                "sort": "updated",
                "direction": "desc",
                "visibility": "all",
            },
        )

        return response.json()

    async def get_repo_details(
        self,
        owner: str,
        repo: str,
    ) -> dict[str, Any]:

        response = await self._get(
            f"{self.BASE_URL}/repos/{owner}/{repo}"
        )

        return response.json()

    async def get_repo_readme(
        self,
        owner: str,
        repo: str,
    ) -> str | None:

        url = f"{self.BASE_URL}/repos/{owner}/{repo}/readme"

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                url,
                headers={
                    **self.headers,
                    "Accept": "application/vnd.github.raw+json",
                },
            )

        if response.status_code == 404:
            return None

        if response.status_code == 401:
            raise GitHubAPIError(
                "GitHub authentication failed."
            )

        if response.status_code >= 400:
            raise GitHubAPIError(
                f"Failed to retrieve README: "
                f"{response.status_code}"
            )

        return response.text

    async def get_repo_tree(
        self,
        owner: str,
        repo: str,
        branch: str,
    ) -> list[str]:

        url = (
            f"{self.BASE_URL}/repos/{owner}/{repo}"
            f"/git/trees/{branch}"
        )

        response = await self._get(
            url,
            params={"recursive": "1"},
        )

        data = response.json()

        return [
            item["path"]
            for item in data.get("tree", [])
            if item.get("type") == "blob"
        ]

    async def get_languages(
        self,
        owner: str,
        repo: str,
    ) -> dict[str, int]:

        response = await self._get(
            f"{self.BASE_URL}/repos/{owner}/{repo}/languages"
        )

        return response.json()