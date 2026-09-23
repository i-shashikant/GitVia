import secrets
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.auth.session import COOKIE_NAME, create_session_token, session_cookie_kwargs
from app.config import get_settings
from app.database import get_db
from app.models import User
from app.security.crypto import encrypt_token

settings = get_settings()

router = APIRouter(
    prefix="/api/auth/github",
    tags=["GitHub Authentication"],
)


def _oauth_configured() -> bool:
    return all(
        [
            settings.github_client_id,
            settings.github_client_secret,
            settings.github_redirect_uri,
            settings.jwt_secret,
        ]
    )


@router.get("")
def github_login():
    if not _oauth_configured():
        raise HTTPException(
            status_code=503,
            detail="GitHub OAuth is not configured",
        )

    state = secrets.token_urlsafe(32)

    params = {
        "client_id": settings.github_client_id,
        "redirect_uri": settings.github_redirect_uri,
        "scope": settings.github_oauth_scope,
        "state": state,
    }

    authorization_url = (
        "https://github.com/login/oauth/authorize?" + urlencode(params)
    )

    response = RedirectResponse(
        url=authorization_url,
        status_code=302,
    )

    response.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=600,
        path="/",
    )

    return response


@router.get("/callback")
async def github_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    db: Session = Depends(get_db),
):
    if not _oauth_configured():
        raise HTTPException(
            status_code=503,
            detail="GitHub OAuth is not configured",
        )

    stored_state = request.cookies.get("oauth_state")

    if not state or not stored_state or state != stored_state:
        raise HTTPException(
            status_code=400,
            detail="Invalid OAuth state",
        )

    if not code:
        raise HTTPException(
            status_code=400,
            detail="Missing authorization code",
        )

    async with httpx.AsyncClient(timeout=20.0) as client:
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": settings.github_client_id,
                "client_secret": settings.github_client_secret,
                "code": code,
                "redirect_uri": settings.github_redirect_uri,
            },
            headers={
                "Accept": "application/json",
            },
        )

        if token_response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail="GitHub token exchange failed",
            )

        token_data = token_response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            raise HTTPException(
                status_code=502,
                detail="GitHub did not return an access token",
            )

        user_response = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github+json",
                "User-Agent": "GitVia-Career-Intelligence",
            },
        )

        if user_response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail="Failed to retrieve GitHub profile",
            )

        github_user = user_response.json()
        email = github_user.get("email")

        email_response = await client.get(
            "https://api.github.com/user/emails",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github+json",
                "User-Agent": "GitVia-Career-Intelligence",
            },
        )

        if email_response.status_code == 200:
            emails = email_response.json()
            primary_email = next(
                (
                    item["email"]
                    for item in emails
                    if item.get("primary") and item.get("verified")
                ),
                None,
            )
            if primary_email:
                email = primary_email

        user = (
            db.query(User)
            .filter(User.github_id == github_user["id"])
            .first()
        )

        encrypted_token = encrypt_token(access_token)

        if user:
            user.github_username = github_user["login"]
            user.name = github_user.get("name")
            user.email = email
            user.avatar_url = github_user.get("avatar_url")
            user.access_token = encrypted_token
        else:
            user = User(
                github_id=github_user["id"],
                github_username=github_user["login"],
                name=github_user.get("name"),
                email=email,
                avatar_url=github_user.get("avatar_url"),
                access_token=encrypted_token,
            )
            db.add(user)

        db.commit()
        db.refresh(user)

    session_token = create_session_token(user)
    response = RedirectResponse(
        url=f"{settings.frontend_url}/auth/success",
        status_code=302,
    )
    response.delete_cookie("oauth_state", path="/")
    response.set_cookie(
        key=COOKIE_NAME,
        value=session_token,
        **session_cookie_kwargs(),
    )
    return response
