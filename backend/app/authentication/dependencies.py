"""
FastAPI dependencies for authentication.

`get_current_user` is the single dependency every protected endpoint should
use. It verifies the Firebase ID token, then upserts a corresponding record
in the `users` collection so the rest of the system (conversations, memory,
documents) can key off a stable `uid`.
"""

from fastapi import Depends, Header
from pymongo.errors import DuplicateKeyError

from app.authentication.firebase import FirebaseUser, verify_id_token
from app.database import get_database
from app.schemas.common import utc_now
from app.schemas.user import UserInDB
from app.utils.exceptions import UnauthorizedError
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _extract_bearer_token(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise UnauthorizedError("Missing or malformed Authorization header.")
    return authorization.split(" ", 1)[1].strip()


async def get_current_user(authorization: str | None = Header(default=None)) -> UserInDB:
    token = _extract_bearer_token(authorization)
    firebase_user: FirebaseUser = verify_id_token(token)

    db = get_database()
    now = utc_now()

    existing = await db["users"].find_one({"uid": firebase_user.uid})
    if existing is None and firebase_user.email:
        existing = await db["users"].find_one({"email": firebase_user.email})

    if existing is None:
        if not firebase_user.email:
            raise UnauthorizedError("Firebase account has no associated email.")

        user = UserInDB(
            uid=firebase_user.uid,
            email=firebase_user.email,
            display_name=firebase_user.display_name,
            photo_url=firebase_user.picture,
            created_at=now,
            last_login_at=now,
        )
        try:
            await db["users"].insert_one(user.model_dump())
        except DuplicateKeyError:
            existing = await db["users"].find_one(
                {"$or": [{"uid": firebase_user.uid}, {"email": firebase_user.email}]}
            )
            if existing is None:
                raise
            return await _heal_and_return(db, existing, firebase_user, now)

        logger.info("user.created", uid=user.uid)
        return user

    return await _heal_and_return(db, existing, firebase_user, now)


async def _heal_and_return(db, existing: dict, firebase_user: FirebaseUser, now) -> UserInDB:
    update_fields = {"last_login_at": now, "display_name": firebase_user.display_name}

    if existing.get("uid") != firebase_user.uid:
        logger.warning(
            "user.uid_mismatch_healed",
            old_uid=existing.get("uid"),
            new_uid=firebase_user.uid,
            email=firebase_user.email,
        )
        update_fields["uid"] = firebase_user.uid

    await db["users"].update_one({"_id": existing["_id"]}, {"$set": update_fields})
    existing.update(update_fields)
    existing.pop("_id", None)
    return UserInDB(**existing)


CurrentUser = Depends(get_current_user)