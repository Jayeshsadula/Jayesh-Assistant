"""
Long-term memory service.

Facts are written to MongoDB (the durable record) and also embedded into
the Chroma "memory" collection (for semantic recall). Short-term memory
(recent conversation turns) is handled separately by ConversationService,
since it doesn't need semantic search — it's just the last N messages.
"""

from typing import List

from app.database import get_database
from app.rag.chroma_client import get_memory_store
from app.schemas.memory import MemoryPublic, MemoryRecord
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MemoryService:
    def __init__(self) -> None:
        self._db = get_database()
        self._store = get_memory_store()

    async def add_memory(self, user_id: str, memory_type: str, content: str) -> MemoryRecord:
        record = MemoryRecord(user_id=user_id, memory_type=memory_type, content=content)
        await self._db["memory"].insert_one(record.model_dump())

        await self._store.add(
            ids=[record.memory_id],
            texts=[content],
            metadatas=[{"user_id": user_id, "memory_type": memory_type}],
        )
        logger.info("memory.added", user_id=user_id, memory_type=memory_type)
        return record

    async def list_memories(self, user_id: str) -> List[MemoryPublic]:
        cursor = self._db["memory"].find({"user_id": user_id}).sort("created_at", -1)
        return [MemoryPublic(**doc) async for doc in cursor]

    async def delete_memory(self, user_id: str, memory_id: str) -> None:
        await self._db["memory"].delete_one({"memory_id": memory_id, "user_id": user_id})
        self._store.delete(ids=[memory_id])

    async def retrieve_relevant_memories(self, user_id: str, query: str, k: int = 4) -> List[str]:
        results = await self._store.query(query_text=query, n_results=k, where={"user_id": user_id})
        return [r["text"] for r in results]
