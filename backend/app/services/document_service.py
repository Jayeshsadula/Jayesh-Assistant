"""Handles validated, sandboxed storage of uploaded files and their DB records."""

import os
import uuid
from pathlib import Path
from typing import List

from fastapi import UploadFile

from app.config import get_settings
from app.database import get_database
from app.rag.chroma_client import get_document_store
from app.schemas.document import DocumentInDB, DocumentPublic
from app.utils.exceptions import FileProcessingError, NotFoundError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentService:
    def __init__(self) -> None:
        self._db = get_database()
        self._settings = get_settings()
        self._store = get_document_store()

    def _validate(self, filename: str, size_bytes: int) -> str:
        suffix = Path(filename).suffix.lower()
        if suffix not in self._settings.allowed_upload_extensions:
            raise FileProcessingError(
                f"File type '{suffix}' is not supported. Allowed: {self._settings.allowed_upload_extensions}"
            )
        if size_bytes > self._settings.max_upload_size_bytes:
            raise FileProcessingError(
                f"File exceeds the maximum upload size of {self._settings.max_upload_size_mb} MB."
            )
        return suffix

    async def save_upload(self, user_id: str, upload: UploadFile) -> DocumentInDB:
        contents = await upload.read()
        suffix = self._validate(upload.filename or "upload", len(contents))

        user_dir = Path(self._settings.upload_dir) / user_id
        user_dir.mkdir(parents=True, exist_ok=True)

        safe_name = f"{uuid.uuid4().hex}{suffix}"
        file_path = user_dir / safe_name
        file_path.write_bytes(contents)

        document = DocumentInDB(
            user_id=user_id,
            filename=upload.filename or safe_name,
            file_path=str(file_path),
            content_type=upload.content_type or "application/octet-stream",
            size_bytes=len(contents),
        )
        await self._db["documents"].insert_one(document.model_dump())
        logger.info("document.uploaded", document_id=document.document_id, user_id=user_id)
        return document

    async def list_documents(self, user_id: str) -> List[DocumentPublic]:
        cursor = self._db["documents"].find({"user_id": user_id}).sort("uploaded_at", -1)
        return [DocumentPublic(**doc) async for doc in cursor]

    async def delete_document(self, user_id: str, document_id: str) -> None:
        doc = await self._db["documents"].find_one({"document_id": document_id, "user_id": user_id})
        if doc is None:
            raise NotFoundError("Document not found.")

        file_path = doc.get("file_path")
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

        self._store.delete_where({"document_id": document_id})
        await self._db["documents"].delete_one({"document_id": document_id, "user_id": user_id})
        logger.info("document.deleted", document_id=document_id)
