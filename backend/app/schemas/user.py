"""User document schema (mirrors the `users` MongoDB collection)."""

from datetime import datetime
from typing import Optional

from pydantic import EmailStr, Field

from app.schemas.common import APIModel, utc_now


class UserInDB(APIModel):
    uid: str = Field(..., description="Firebase UID — primary identifier for the user")
    email: EmailStr
    display_name: Optional[str] = None
    photo_url: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)
    last_login_at: datetime = Field(default_factory=utc_now)
    is_active: bool = True


class UserPublic(APIModel):
    uid: str
    email: EmailStr
    display_name: Optional[str] = None
    photo_url: Optional[str] = None
    created_at: datetime
