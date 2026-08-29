import os
import secrets
from urllib.parse import urlencode

import httpx
import jwt
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from fastapi.responses import RedirectResponse

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
def github_login(response: Response):
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

    redirect = RedirectResponse(
        url=authorization_url,
        status_code=302,
    )

    redirect.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        secure=False,  # True in production
        samesite="lax",
        max_age=600,
    )

    return redirect


@router.get("/callback")
async def github_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    db: Session = Depends(get_db),
):
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

    async with httpx.AsyncClient() as client:

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

        user_response = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github+json",
            },
        )

        if user_response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail="Failed to retrieve GitHub profile",
            )

        github_user = user_response.json()

        # Find existing GitVia user
    user = (
        db.query(User)
        .filter(User.github_id == github_user["id"])
        .first()
    )

    if user:
        # Update existing user's GitHub information
        user.github_username = github_user["login"]
        user.name = github_user.get("name")
        user.avatar_url = github_user.get("avatar_url")

    else:
        # Create a new GitVia user
        user = User(
            github_id=github_user["id"],
            github_username=github_user["login"],
            name=github_user.get("name"),
            avatar_url=github_user.get("avatar_url"),
        )

        db.add(user)

    db.commit()
    db.refresh(user)

    session_token = jwt.encode(
        {
            "user_id": user.id,
            "github_id": user.github_id,
            "github_login": user.github_username,
        },
        JWT_SECRET,
        algorithm="HS256",
    )

    response = RedirectResponse(
        url="http://localhost:3000/auth/success",
        status_code=302,
    )

    response.delete_cookie("oauth_state")

    response.set_cookie(
        key="gitvia_session",
        value=session_token,
        httponly=True,
        secure=False,  # True in production
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )

    return response