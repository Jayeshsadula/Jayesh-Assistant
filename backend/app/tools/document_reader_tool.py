"""Document reader tool — returns the full extracted text of a specific uploaded document."""

from typing import Any, Dict

from app.database import get_database
from app.rag.extractors import extract_text
from app.tools.base import BaseTool

MAX_CHARS_RETURNED = 6000


class DocumentReaderTool(BaseTool):
    name = "document_reader"
    description = (
        "Read the full text content of a specific document the user has uploaded, "
        "identified by its document_id. Use this when the user refers to a document by "
        "name and wants more than a small retrieved snippet."
    )

    def __init__(self) -> None:
        self._db = get_database()

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "document_id": {"type": "string", "description": "The document's unique ID."}
            },
            "required": ["document_id"],
        }

    async def run(self, document_id: str) -> str:
        doc = await self._db["documents"].find_one({"document_id": document_id})
        if doc is None:
            return f"No document found with id '{document_id}'."

        file_path = doc.get("file_path")
        if not file_path:
            return "Document metadata is missing its file path."

        text = extract_text(file_path, doc.get("content_type", ""))
        return text[:MAX_CHARS_RETURNED]
