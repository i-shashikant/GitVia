from fastapi import FastAPI
from sqlalchemy import text

from app.database import Base, engine
from app import models
from app.auth.github import router as github_auth_router
from app.auth.session import router as session_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="GitVia API",
    description="AI-powered GitHub career intelligence platform",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(github_auth_router)
app.include_router(session_router)


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "gitvia-api",
    }


@app.get("/api/health/db")
def database_health_check():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        value = result.scalar()

    return {
        "status": "ok",
        "database": "connected",
        "test": value,
    }