from typing import Any

from sqlalchemy.orm import Session

from app.github.client import GitHubAPIError
from app.models import User
from app.services.analysis import get_developer_context


async def build_developer_context(
    current_user: User,
    db: Session,
    refresh: bool = False,
) -> dict[str, Any]:
    if not current_user.access_token:
        raise GitHubAPIError("GitHub account is not connected")

    return await get_developer_context(db, current_user, refresh=refresh)
