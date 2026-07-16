"""Long-term memory schemas (mirrors the `memory` collection + ChromaDB vectors)."""

from datetime import datetime
from typing import Optional

from pydantic import Field

from app.schemas.common import APIModel, MemoryType, new_id, utc_now


class MemoryRecord(APIModel):
    memory_id: str = Field(default_factory=new_id)
    user_id: str
    memory_type: MemoryType
    content: str = Field(..., description="The fact/preference/interest text, embedded for semantic search")
    source_conversation_id: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class MemoryCreateRequest(APIModel):
    memory_type: MemoryType
    content: str = Field(..., min_length=1, max_length=2000)


class MemoryPublic(APIModel):
    memory_id: str
    memory_type: MemoryType
    content: str
    created_at: datetime
