"""Document schemas (mirrors the `documents` collection)."""

from datetime import datetime
from typing import Optional

from pydantic import Field

from app.schemas.common import APIModel, DocumentStatus, new_id, utc_now


class DocumentInDB(APIModel):
    document_id: str = Field(default_factory=new_id)
    user_id: str
    filename: str
    file_path: str
    content_type: str
    size_bytes: int
    status: DocumentStatus = DocumentStatus.PROCESSING
    chunk_count: int = 0
    error_message: Optional[str] = None
    uploaded_at: datetime = Field(default_factory=utc_now)


class DocumentPublic(APIModel):
    document_id: str
    filename: str
    content_type: str
    size_bytes: int
    status: DocumentStatus
    chunk_count: int
    uploaded_at: datetime
