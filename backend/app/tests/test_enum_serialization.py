"""
Regression test for a real bug: APIModel sets `use_enum_values=True`, which means
enum-typed fields (e.g. ChatRequest.model) are stored as plain strings after
validation — NOT as enum members. Code that calls `.value` on them raises
AttributeError. This test locks in the expected (string) behavior so that
assumption can't silently break again.
"""

from app.schemas.common import MemoryType, ModelName
from app.schemas.conversation import ChatRequest, ConversationCreateRequest
from app.schemas.memory import MemoryCreateRequest


def test_chat_request_model_field_is_plain_string_not_enum():
    payload = ChatRequest(message="hello", model=ModelName.LLAMA)
    assert payload.model == "llama3.1:8b"
    assert isinstance(payload.model, str)
    assert not hasattr(payload.model, "value")


def test_conversation_create_request_model_field_is_plain_string():
    payload = ConversationCreateRequest(model=ModelName.MISTRAL)
    assert payload.model == "mistral:7b"
    assert isinstance(payload.model, str)


def test_memory_create_request_type_field_is_plain_string():
    payload = MemoryCreateRequest(memory_type=MemoryType.FACT, content="likes tea")
    assert payload.memory_type == "fact"
    assert isinstance(payload.memory_type, str)
