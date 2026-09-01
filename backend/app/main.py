from fastapi import FastAPI
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app import models
from app.auth.github import router as github_auth_router
from app.auth.session import router as session_router
from app.routers.profile import router as profile_router
from app.routers.repos import router as repos_router
from app.routers.career import router as career_router
from app.routers.roadmap import router as roadmap_router
from app.routers.chat import router as chat_router


app = FastAPI(
    title="GitVia API",
    description="AI-powered GitHub career intelligence platform",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
            "status": "fallback",
            "database": "sqlite_local",
            "detail": str(e)
        }