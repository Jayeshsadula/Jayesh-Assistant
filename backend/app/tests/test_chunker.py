"""Unit tests for app.rag.chunker."""

import pytest

from app.rag.chunker import chunk_text, normalize_whitespace


def test_normalize_whitespace_collapses_and_trims():
    assert normalize_whitespace("  hello   \n\n world  ") == "hello world"


def test_chunk_text_empty_string_returns_empty_list():
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_chunk_text_shorter_than_chunk_size_returns_single_chunk():
    text = "This is a short piece of text."
    chunks = chunk_text(text, chunk_size=1000, chunk_overlap=100)
    assert chunks == [text]


def test_chunk_text_splits_long_text_into_multiple_chunks():
    text = " ".join(["word"] * 500)  # 500 words, well over 1000 chars
    chunks = chunk_text(text, chunk_size=200, chunk_overlap=20)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 200


def test_chunk_text_overlap_shares_content_between_consecutive_chunks():
    text = " ".join(f"word{i}" for i in range(200))
    chunks = chunk_text(text, chunk_size=100, chunk_overlap=30)
    assert len(chunks) > 1
    # Overlap means some trailing words of chunk[i] should reappear at the start of chunk[i+1]
    first_words = set(chunks[0].split()[-2:])
    second_words = set(chunks[1].split()[:4])
    assert first_words & second_words


def test_chunk_text_rejects_overlap_greater_or_equal_to_chunk_size():
    with pytest.raises(ValueError):
        chunk_text("some text", chunk_size=50, chunk_overlap=50)
