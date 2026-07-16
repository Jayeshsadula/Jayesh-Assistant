"""Model listing endpoint — reports which local Ollama models are configured/available."""

from fastapi import APIRouter, Depends

from app.authentication.dependencies import CurrentUser
from app.config import get_settings
from app.llm.ollama_client import get_ollama_client
from app.schemas.user import UserInDB

router = APIRouter()


@router.get("/models", tags=["models"])
async def list_models(current_user: UserInDB = CurrentUser) -> dict:
    settings = get_settings()
    client = get_ollama_client()

    pulled_models = await client.list_models()
    configured_models = settings.ollama_available_models

    return {
        "configured_models": configured_models,
        "pulled_models": pulled_models,
        "default_model": settings.ollama_default_model,
        "ready_models": [m for m in configured_models if any(m in p for p in pulled_models)],
    }
