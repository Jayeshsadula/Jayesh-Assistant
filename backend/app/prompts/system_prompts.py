"""
System prompt templates.

Keeping these as plain functions (not scattered string literals) makes it
easy to unit test prompt construction and to keep the orchestrator's
context-building logic readable.
"""

from typing import List, Optional

BASE_SYSTEM_PROMPT = (
    "You are JAYESH Assistant, a private, self-hosted AI assistant. "
    "You run entirely on local infrastructure and never send data to third-party APIs. "
    "Be direct, helpful, and honest. If you don't know something, say so instead of guessing. "
    "Format responses in Markdown when it improves readability (code blocks, lists, tables)."
)


def build_system_prompt(
    memory_snippets: Optional[List[str]] = None,
    document_snippets: Optional[List[str]] = None,
) -> str:
    """Assemble the final system prompt from the base prompt plus retrieved context."""
    sections = [BASE_SYSTEM_PROMPT]

    if memory_snippets:
        memory_block = "\n".join(f"- {snippet}" for snippet in memory_snippets)
        sections.append(
            "Relevant information you remember about this user:\n" + memory_block
        )

    if document_snippets:
        doc_block = "\n\n".join(document_snippets)
        sections.append(
            "Relevant excerpts from the user's uploaded documents "
            "(use them to answer if relevant, and mention you're citing an uploaded document):\n"
            + doc_block
        )

    return "\n\n".join(sections)
