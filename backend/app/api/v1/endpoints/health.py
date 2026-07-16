"""Health check endpoint — used for uptime monitoring and load balancers."""

from fastapi import APIRouter

from app.config import get_settings

router = APIRouter()


@router.get("/health", tags=["health"])
async def health_check() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "environment": settings.app_env,
    }
