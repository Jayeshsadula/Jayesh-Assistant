"""Orchestrates the document ingestion pipeline: extract -> chunk -> embed -> index."""

from typing import List

from app.database import get_database
from app.rag.chroma_client import get_document_store
from app.rag.chunker import chunk_text
from app.rag.extractors import extract_text
from app.schemas.common import DocumentStatus
from app.utils.logger import get_logger

logger = get_logger(__name__)


class IngestionService:
    def __init__(self) -> None:
        self._db = get_database()
        self._store = get_document_store()

    async def ingest(self, document_id: str, user_id: str, file_path: str, content_type: str) -> None:
        try:
            raw_text = extract_text(file_path, content_type)
            chunks: List[str] = chunk_text(raw_text)

            if not chunks:
                await self._mark_failed(document_id, "No extractable text found in document.")
                return

            ids = [f"{document_id}:{i}" for i in range(len(chunks))]
            metadatas = [
                {"document_id": document_id, "user_id": user_id, "chunk_index": i}
                for i in range(len(chunks))
            ]

            await self._store.add(ids=ids, texts=chunks, metadatas=metadatas)

            await self._db["documents"].update_one(
                {"document_id": document_id},
                {"$set": {"status": DocumentStatus.READY.value, "chunk_count": len(chunks)}},
            )
            logger.info("rag.ingested", document_id=document_id, chunks=len(chunks))

        except Exception as exc:  # noqa: BLE001
            logger.error("rag.ingestion_failed", document_id=document_id, error=str(exc))
            await self._mark_failed(document_id, str(exc))

    async def _mark_failed(self, document_id: str, error_message: str) -> None:
        await self._db["documents"].update_one(
            {"document_id": document_id},
            {"$set": {"status": DocumentStatus.FAILED.value, "error_message": error_message}},
        )

    async def retrieve_context(self, query: str, user_id: str, document_ids: List[str], k: int = 4) -> List[str]:
        if not document_ids:
            where = {"user_id": user_id}
        else:
            where = {"document_id": {"$in": document_ids}}

        results = await self._store.query(query_text=query, n_results=k, where=where)
        return [r["text"] for r in results]
