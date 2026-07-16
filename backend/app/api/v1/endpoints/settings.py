"""User settings endpoints."""

from fastapi import APIRouter

from app.authentication.dependencies import CurrentUser
from app.schemas.settings_schema import UserSettingsPublic, UserSettingsUpdateRequest
from app.schemas.user import UserInDB
from app.services.settings_service import SettingsService

router = APIRouter()


@router.get("/settings", response_model=UserSettingsPublic, tags=["settings"])
async def get_settings_endpoint(current_user: UserInDB = CurrentUser) -> UserSettingsPublic:
    service = SettingsService()
    settings = await service.get_settings(user_id=current_user.uid)
    return UserSettingsPublic(**settings.model_dump())


@router.put("/settings", response_model=UserSettingsPublic, tags=["settings"])
async def update_settings_endpoint(
    payload: UserSettingsUpdateRequest, current_user: UserInDB = CurrentUser
) -> UserSettingsPublic:
    service = SettingsService()
    settings = await service.update_settings(user_id=current_user.uid, payload=payload)
    return UserSettingsPublic(**settings.model_dump())
