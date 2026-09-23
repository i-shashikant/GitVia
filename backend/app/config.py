import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


def _bool(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def _csv(name: str, default: str) -> list[str]:
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


class Settings:
    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./gitvia.db")
        self.auto_create_tables = _bool("AUTO_CREATE_TABLES", "true")

        self.github_client_id = os.getenv("GITHUB_CLIENT_ID", "")
        self.github_client_secret = os.getenv("GITHUB_CLIENT_SECRET", "")
        self.github_redirect_uri = os.getenv(
            "GITHUB_REDIRECT_URI",
            "http://localhost:8000/api/auth/github/callback",
        )
        self.github_oauth_scope = os.getenv(
            "GITHUB_OAUTH_SCOPE",
            "read:user user:email public_repo",
        )

        self.jwt_secret = os.getenv("JWT_SECRET", "")
        self.jwt_expire_hours = int(os.getenv("JWT_EXPIRE_HOURS", "168"))
        self.encryption_key = os.getenv("ENCRYPTION_KEY", "")

        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000").rstrip("/")
        self.cors_origins = _csv("CORS_ORIGINS", self.frontend_url)
        self.cookie_secure = _bool("COOKIE_SECURE", "false")
        self.cookie_samesite = os.getenv("COOKIE_SAMESITE", "lax")

        self.analysis_concurrency = int(os.getenv("ANALYSIS_CONCURRENCY", "4"))
        self.skip_forks = _bool("SKIP_FORKS", "true")
        self.skip_archived = _bool("SKIP_ARCHIVED", "true")
        self.max_tree_paths = int(os.getenv("MAX_TREE_PATHS", "2500"))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
