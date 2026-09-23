from fastapi import FastAPI
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine
from app import models  # noqa: F401
from app.auth.github import router as github_auth_router
from app.auth.session import router as session_router
from app.routers.profile import router as profile_router
from app.routers.repos import router as repos_router
from app.routers.career import router as career_router
from app.routers.roadmap import router as roadmap_router
from app.routers.chat import router as chat_router

settings = get_settings()

app = FastAPI(
    title="GitVia API",
    description="Evidence-based GitHub career intelligence platform",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.auto_create_tables:
    Base.metadata.create_all(bind=engine)

app.include_router(github_auth_router)
app.include_router(session_router)
app.include_router(profile_router)
app.include_router(repos_router)
app.include_router(career_router)
app.include_router(roadmap_router)
app.include_router(chat_router)


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "gitvia-api",
    }


@app.get("/api/health/db")
def database_health_check():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            value = result.scalar()

        return {
            "status": "ok",
            "database": "connected",
            "test": value,
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "unavailable",
            "detail": str(e),
        }
