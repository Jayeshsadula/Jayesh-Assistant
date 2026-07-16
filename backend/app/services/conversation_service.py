"""Business logic for creating, listing, renaming, and deleting conversations."""

from typing import List, Optional

from app.database import get_database
from app.schemas.common import MessageRole, utc_now
from app.schemas.conversation import (
    ConversationInDB,
    ConversationPublic,
    MessageInDB,
    MessagePublic,
)
from app.utils.exceptions import NotFoundError
from app.utils.logger import get_logger

logger = get_logger(__name__)

MAX_HISTORY_MESSAGES = 20


class ConversationService:
    def __init__(self) -> None:
        self._db = get_database()

    async def create_conversation(self, user_id: str, title: str, model: str) -> ConversationInDB:
        conversation = ConversationInDB(user_id=user_id, title=title, model=model)
        await self._db["conversations"].insert_one(conversation.model_dump())
        logger.info("conversation.created", conversation_id=conversation.conversation_id, user_id=user_id)
        return conversation

    async def get_conversation(self, conversation_id: str, user_id: str) -> ConversationInDB:
        doc = await self._db["conversations"].find_one(
            {"conversation_id": conversation_id, "user_id": user_id}
        )
        if doc is None:
            raise NotFoundError("Conversation not found.")
        return ConversationInDB(**doc)

    async def list_conversations(self, user_id: str, search: Optional[str] = None) -> List[ConversationPublic]:
        query: dict = {"user_id": user_id, "is_archived": False}
        if search:
            query["title"] = {"$regex": search, "$options": "i"}

        cursor = self._db["conversations"].find(query).sort("updated_at", -1)
        results = [ConversationPublic(**doc) async for doc in cursor]
        return results

    async def rename_conversation(self, conversation_id: str, user_id: str, title: str) -> ConversationPublic:
        result = await self._db["conversations"].find_one_and_update(
            {"conversation_id": conversation_id, "user_id": user_id},
            {"$set": {"title": title, "updated_at": utc_now()}},
            return_document=True,
        )
        if result is None:
            raise NotFoundError("Conversation not found.")
        return ConversationPublic(**result)

    async def delete_conversation(self, conversation_id: str, user_id: str) -> None:
        result = await self._db["conversations"].delete_one(
            {"conversation_id": conversation_id, "user_id": user_id}
        )
        if result.deleted_count == 0:
            raise NotFoundError("Conversation not found.")
        await self._db["messages"].delete_many({"conversation_id": conversation_id})
        logger.info("conversation.deleted", conversation_id=conversation_id)

    async def touch_conversation(self, conversation_id: str) -> None:
        await self._db["conversations"].update_one(
            {"conversation_id": conversation_id}, {"$set": {"updated_at": utc_now()}}
        )

    async def maybe_set_title_from_first_message(self, conversation_id: str, message: str) -> None:
        conversation = await self._db["conversations"].find_one({"conversation_id": conversation_id})
        if conversation and conversation.get("title") == "New Chat":
            title = message.strip().splitlines()[0][:60]
            await self._db["conversations"].update_one(
                {"conversation_id": conversation_id}, {"$set": {"title": title or "New Chat"}}
            )

    async def add_message(
        self,
        conversation_id: str,
        role: MessageRole,
        content: str,
        model_used: Optional[str] = None,
    ) -> MessageInDB:
        message = MessageInDB(
            conversation_id=conversation_id,
            role=role,
            content=content,
            model_used=model_used,
        )
        await self._db["messages"].insert_one(message.model_dump())
        return message

    async def get_recent_messages(self, conversation_id: str, limit: int = MAX_HISTORY_MESSAGES) -> List[MessageInDB]:
        cursor = (
            self._db["messages"]
            .find({"conversation_id": conversation_id})
            .sort("created_at", -1)
            .limit(limit)
        )
        docs = [doc async for doc in cursor]
        docs.reverse()
        return [MessageInDB(**doc) for doc in docs]

    async def list_messages(self, conversation_id: str) -> List[MessagePublic]:
        cursor = self._db["messages"].find({"conversation_id": conversation_id}).sort("created_at", 1)
        return [MessagePublic(**doc) async for doc in cursor]
