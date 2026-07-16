"""
Server-Sent Event formatting helpers.

The frontend's EventSource-style client expects each event as a small JSON
payload with a `type` discriminator: "token", "done", or "error". Keeping
the wire format centralized here means the chat endpoint doesn't need to
hand-format SSE strings inline.
"""

import json
from typing import Any, AsyncGenerator, Dict


def format_sse(event_type: str, data: Dict[str, Any]) -> str:
    payload = json.dumps({"type": event_type, **data})
    return f"data: {payload}\n\n"


async def sse_token_stream(
    token_generator: AsyncGenerator[str, None],
    conversation_id: str,
) -> AsyncGenerator[str, None]:
    """Wrap a raw token generator into properly formatted SSE frames.

    Emits:
      - one "token" event per generated token
      - a final "done" event with the full conversation_id
      - an "error" event (and stops) if the underlying generator raises
    """
    full_text_parts = []
    try:
        async for token in token_generator:
            full_text_parts.append(token)
            yield format_sse("token", {"content": token})
    except Exception as exc:  # noqa: BLE001 - deliberately broad to always notify the client
        yield format_sse("error", {"message": str(exc)})
        return

    yield format_sse(
        "done",
        {"conversation_id": conversation_id, "full_text": "".join(full_text_parts)},
    )
