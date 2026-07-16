"""Conversation and message schemas (mirrors `conversations` and `messages` collections)."""

from datetime import datetime
from typing import List, Optional

from pydantic import Field

from app.schemas.common import APIModel, MessageRole, ModelName, new_id, utc_now


class MessageInDB(APIModel):
    message_id: str = Field(default_factory=new_id)
    conversation_id: str
    role: MessageRole
    content: str
    model_used: Optional[str] = None
    tool_calls: List[dict] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)


class MessagePublic(APIModel):
    message_id: str
    role: MessageRole
    content: str
    model_used: Optional[str] = None
    created_at: datetime


class ConversationInDB(APIModel):
    conversation_id: str = Field(default_factory=new_id)
    user_id: str
    title: str = "New Chat"
    model: str = ModelName.QWEN.value
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    is_archived: bool = False


class ConversationPublic(APIModel):
    conversation_id: str
    title: str
    model: str
    created_at: datetime
    updated_at: datetime


class ConversationCreateRequest(APIModel):
    title: Optional[str] = Field(default="New Chat", max_length=200)
    model: ModelName = ModelName.QWEN


class ConversationRenameRequest(APIModel):
    title: str = Field(..., min_length=1, max_length=200)


class ChatRequest(APIModel):
    conversation_id: Optional[str] = Field(
        default=None, description="Omit to create a new conversation"
    )
    message: str = Field(..., min_length=1, max_length=32000)
    model: ModelName = ModelName.QWEN
    use_memory: bool = True
    use_rag: bool = True
    document_ids: List[str] = Field(default_factory=list)


class ChatResponse(APIModel):
    conversation_id: str
    message: MessagePublic
