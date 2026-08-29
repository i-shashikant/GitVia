from fastapi import FastAPI
from sqlalchemy import text

from app.database import engine

app = FastAPI(
    title="GitVia API",
    description="AI-powered GitHub career intelligence platform",
    version="0.1.0",
)


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