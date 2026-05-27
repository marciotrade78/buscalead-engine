from fastapi import APIRouter

from app.api.routes import health, jobs, leads, pipeline

api_router = APIRouter()


@api_router.get("")
async def api_index() -> dict:
    return {
        "name": "Busca Lead API",
        "docs": "/docs",
        "health": "/api/v1/health",
        "streamlit": "http://127.0.0.1:8501",
        "post_endpoints": [
            "/api/v1/leads/search",
            "/api/v1/leads/search/preview",
            "/api/v1/leads/{lead_id}/analyze",
        ],
    }


api_router.include_router(health.router, tags=["health"])
api_router.include_router(leads.router, prefix="/leads", tags=["leads"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(pipeline.router, prefix="/pipeline", tags=["pipeline"])
