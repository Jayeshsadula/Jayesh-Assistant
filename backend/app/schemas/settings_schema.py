"""User-configurable settings schema (mirrors the `settings` collection)."""

from datetime import datetime

from pydantic import Field

from app.schemas.common import APIModel, ModelName, ThemePreference, utc_now


class UserSettingsInDB(APIModel):
    user_id: str
    theme: ThemePreference = ThemePreference.SYSTEM
    default_model: ModelName = ModelName.QWEN
    memory_enabled: bool = True
    rag_enabled: bool = True
    updated_at: datetime = Field(default_factory=utc_now)


class UserSettingsUpdateRequest(APIModel):
    theme: ThemePreference | None = None
    default_model: ModelName | None = None
    memory_enabled: bool | None = None
    rag_enabled: bool | None = None


class UserSettingsPublic(APIModel):
    theme: ThemePreference
    default_model: ModelName
    memory_enabled: bool
    rag_enabled: bool
