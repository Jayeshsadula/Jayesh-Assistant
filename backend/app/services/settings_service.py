"""User settings service (theme, default model, memory/RAG toggles)."""

from app.database import get_database
from app.schemas.common import utc_now
from app.schemas.settings_schema import UserSettingsInDB, UserSettingsUpdateRequest


class SettingsService:
    def __init__(self) -> None:
        self._db = get_database()

    async def get_settings(self, user_id: str) -> UserSettingsInDB:
        doc = await self._db["settings"].find_one({"user_id": user_id})
        if doc is None:
            defaults = UserSettingsInDB(user_id=user_id)
            await self._db["settings"].insert_one(defaults.model_dump())
            return defaults
        return UserSettingsInDB(**doc)

    async def update_settings(self, user_id: str, payload: UserSettingsUpdateRequest) -> UserSettingsInDB:
        updates = {k: v for k, v in payload.model_dump(exclude_none=True).items()}
        updates["updated_at"] = utc_now()

        await self._db["settings"].update_one(
            {"user_id": user_id}, {"$set": updates, "$setOnInsert": {"user_id": user_id}}, upsert=True
        )
        doc = await self._db["settings"].find_one({"user_id": user_id})
        return UserSettingsInDB(**doc)
