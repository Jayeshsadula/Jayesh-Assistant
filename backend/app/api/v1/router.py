"""Aggregates all v1 endpoint routers under a single APIRouter."""

from fastapi import APIRouter

from app.api.v1.endpoints import chat, conversations, documents, health, memory, models, settings

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(chat.router)
api_router.include_router(conversations.router)
api_router.include_router(memory.router)
api_router.include_router(documents.router)
api_router.include_router(models.router)
api_router.include_router(settings.router)
