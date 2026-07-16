"""Unit tests for app.streaming.sse."""

import json

import pytest

from app.streaming.sse import format_sse, sse_token_stream


def test_format_sse_shape():
    frame = format_sse("token", {"content": "hello"})
    assert frame.startswith("data: ")
    assert frame.endswith("\n\n")
    payload = json.loads(frame[len("data: "):].strip())
    assert payload == {"type": "token", "content": "hello"}


async def _gen(tokens):
    for t in tokens:
        yield t


@pytest.mark.asyncio
async def test_sse_token_stream_emits_tokens_then_done():
    async def gen():
        for t in ["Hel", "lo"]:
            yield t

    frames = [f async for f in sse_token_stream(gen(), conversation_id="conv-1")]
    assert len(frames) == 3  # 2 tokens + 1 done

    first = json.loads(frames[0][len("data: "):].strip())
    second = json.loads(frames[1][len("data: "):].strip())
    last = json.loads(frames[2][len("data: "):].strip())

    assert first == {"type": "token", "content": "Hel"}
    assert second == {"type": "token", "content": "lo"}
    assert last["type"] == "done"
    assert last["conversation_id"] == "conv-1"
    assert last["full_text"] == "Hello"


@pytest.mark.asyncio
async def test_sse_token_stream_emits_error_on_exception():
    async def gen():
        yield "partial"
        raise RuntimeError("upstream failed")

    frames = [f async for f in sse_token_stream(gen(), conversation_id="conv-2")]
    last = json.loads(frames[-1][len("data: "):].strip())
    assert last["type"] == "error"
    assert "upstream failed" in last["message"]
