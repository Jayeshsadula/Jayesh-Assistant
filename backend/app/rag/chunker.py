"""Text chunking for RAG ingestion.

Uses a simple, dependency-light sliding-window splitter on whitespace-normalized
text. Chunk size and overlap are tuned for typical embedding-model context
windows (nomic-embed-text handles ~8k tokens, but shorter chunks retrieve
more precisely).
"""

import re
from typing import List

DEFAULT_CHUNK_SIZE = 1000  # characters
DEFAULT_CHUNK_OVERLAP = 150  # characters


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[str]:
    text = normalize_whitespace(text)
    if not text:
        return []

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    chunks: List[str] = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        # Prefer breaking on a sentence/space boundary rather than mid-word.
        if end < text_length:
            boundary = text.rfind(" ", start, end)
            if boundary > start:
                end = boundary

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break
        start = max(end - chunk_overlap, start + 1)

    return chunks
