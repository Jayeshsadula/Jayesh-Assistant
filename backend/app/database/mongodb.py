"""
MongoDB connection lifecycle management.

A single AsyncIOMotorClient is created at application startup and reused
for the lifetime of the process. FastAPI's lifespan handler in app.main
calls connect_to_mongo() / close_mongo_connection() around the app's life.
"""

from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None


mongodb = MongoDB()


async def connect_to_mongo() -> None:
    settings = get_settings()
    logger.info("mongodb.connecting", uri=settings.mongodb_uri, db=settings.mongodb_db_name)

    mongodb.client = AsyncIOMotorClient(settings.mongodb_uri, uuidRepresentation="standard")
    mongodb.db = mongodb.client[settings.mongodb_db_name]

    # Fail fast if Mongo is unreachable rather than discovering it on first request.
    await mongodb.client.admin.command("ping")
    logger.info("mongodb.connected")

    await _ensure_indexes()


async def close_mongo_connection() -> None:
    if mongodb.client is not None:
        mongodb.client.close()
        logger.info("mongodb.connection_closed")


def get_database() -> AsyncIOMotorDatabase:
    if mongodb.db is None:
        raise RuntimeError("MongoDB has not been initialized. Call connect_to_mongo() first.")
    return mongodb.db


async def _ensure_indexes() -> None:
    """Create indexes required for correctness and query performance."""
    db = get_database()

    await db["users"].create_index("uid", unique=True)
    await db["users"].create_index("email", unique=True)

    await db["conversations"].create_index([("user_id", 1), ("updated_at", -1)])
    await db["conversations"].create_index("conversation_id", unique=True)

    await db["messages"].create_index([("conversation_id", 1), ("created_at", 1)])
    await db["messages"].create_index("message_id", unique=True)

    await db["memory"].create_index([("user_id", 1), ("memory_type", 1)])
    await db["memory"].create_index("memory_id", unique=True)

    await db["documents"].create_index([("user_id", 1), ("uploaded_at", -1)])
    await db["documents"].create_index("document_id", unique=True)

    await db["settings"].create_index("user_id", unique=True)

    await db["audit_logs"].create_index([("user_id", 1), ("created_at", -1)])

    logger.info("mongodb.indexes_ensured")
