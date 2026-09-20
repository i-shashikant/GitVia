import os
import secrets
from urllib.parse import urlencode

import httpx
import jwt
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User

load_dotenv()

router = APIRouter(
    prefix="/api/auth/github",
    tags=["GitHub Authentication"],
)

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI")
JWT_SECRET = os.getenv("JWT_SECRET")

if not all(
    [
        GITHUB_CLIENT_ID,
        GITHUB_CLIENT_SECRET,
        GITHUB_REDIRECT_URI,
        JWT_SECRET,
    ]
):
    raise RuntimeError("Missing required environment variables")


@router.get("")
def github_login():
    state = secrets.token_urlsafe(32)

    params = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": GITHUB_REDIRECT_URI,
        "scope": "read:user user:email",
        "state": state,
    }

    authorization_url = (
        "https://github.com/login/oauth/authorize?"
        + urlencode(params)
    )

    response = RedirectResponse(
        url=authorization_url,
        status_code=302,
    )

    response.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=600,
    )

    return response


@router.get("/callback")
async def github_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    db: Session = Depends(get_db),
):
    # ---------------------------------------------------------
    # 1. Validate OAuth state
    # ---------------------------------------------------------

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

        # -----------------------------------------------------
        # 2. Exchange GitHub authorization code for token
        # -----------------------------------------------------

        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": GITHUB_REDIRECT_URI,
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

        # -----------------------------------------------------
        # 3. Retrieve authenticated GitHub user
        # -----------------------------------------------------

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

        # -----------------------------------------------------
        # 4. Retrieve GitHub email
        # -----------------------------------------------------

        email = github_user.get("email")

        if not email:
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

        # -----------------------------------------------------
        # 5. Find existing GitVia user
        # -----------------------------------------------------

        user = (
            db.query(User)
            .filter(User.github_id == github_user["id"])
            .first()
        )

        if user:
            # Existing user
            user.github_username = github_user["login"]
            user.name = github_user.get("name")
            user.email = github_user.get("email")
            user.avatar_url = github_user.get("avatar_url")

            # IMPORTANT:
            # Store the GitHub OAuth token so the rest of
            # GitVia can access this user's GitHub account.
            user.access_token = access_token

        else:
            # New user
            user = User(
                github_id=github_user["id"],
                github_username=github_user["login"],
                name=github_user.get("name"),
                email=github_user.get("email"),
                avatar_url=github_user.get("avatar_url"),
                access_token=access_token,
            )

            db.add(user)

        db.commit()
        db.refresh(user)

    # ---------------------------------------------------------
    # 6. Create GitVia session JWT
    # ---------------------------------------------------------

    session_token = jwt.encode(
        {
            "user_id": user.id,
            "github_id": user.github_id,
            "github_login": user.github_username,
        },
        JWT_SECRET,
        algorithm="HS256",
    )

    # ---------------------------------------------------------
    # 7. Redirect to frontend
    # ---------------------------------------------------------

    response = RedirectResponse(
        url="http://localhost:3000/auth/success",
        status_code=302,
    )

    response.delete_cookie("oauth_state")

    response.set_cookie(
        key="gitvia_session",
        value=session_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )

    return response