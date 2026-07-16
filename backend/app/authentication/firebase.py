"""
Firebase Admin SDK integration.

The frontend authenticates users with Firebase Authentication (email/password,
Google, etc.) and sends the resulting Firebase ID token to the backend on
every request via the `Authorization: Bearer <token>` header. This module
verifies that token server-side — it never trusts a client-supplied UID.
"""

from dataclasses import dataclass
from functools import lru_cache

import firebase_admin
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials
from firebase_admin.exceptions import FirebaseError

from app.config import get_settings
from app.utils.exceptions import UnauthorizedError
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class FirebaseUser:
    uid: str
    email: str | None
    display_name: str | None
    picture: str | None


@lru_cache
def _init_firebase_app() -> firebase_admin.App:
    settings = get_settings()
    cred = credentials.Certificate(settings.firebase_credentials_path)
    logger.info("firebase.initializing", project_id=settings.firebase_project_id)
    return firebase_admin.initialize_app(
        cred, options={"projectId": settings.firebase_project_id}
    )


def verify_id_token(id_token: str) -> FirebaseUser:
    """Verify a Firebase ID token and return the authenticated user's claims.

    Raises UnauthorizedError if the token is missing, expired, or invalid.
    """
    _init_firebase_app()

    if not id_token:
        raise UnauthorizedError("Missing authentication token.")

    try:
        decoded = firebase_auth.verify_id_token(id_token, check_revoked=True)
    except firebase_auth.RevokedIdTokenError as exc:
        raise UnauthorizedError("Token has been revoked. Please sign in again.") from exc
    except firebase_auth.ExpiredIdTokenError as exc:
        raise UnauthorizedError("Token has expired. Please sign in again.") from exc
    except firebase_auth.InvalidIdTokenError as exc:
        raise UnauthorizedError("Invalid authentication token.") from exc
    except FirebaseError as exc:
        logger.error("firebase.verify_failed", error=str(exc))
        raise UnauthorizedError("Could not verify authentication token.") from exc

    return FirebaseUser(
        uid=decoded["uid"],
        email=decoded.get("email"),
        display_name=decoded.get("name"),
        picture=decoded.get("picture"),
    )
