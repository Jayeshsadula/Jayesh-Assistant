"""Shared enums and base model utilities used across schemas."""

from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_id() -> str:
    return str(uuid4())


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class MemoryType(str, Enum):
    PREFERENCE = "preference"
    INTEREST = "interest"
    PROJECT = "project"
    FACT = "fact"


class ModelName(str, Enum):
    QWEN = "qwen2.5:7b"
    LLAMA = "llama3.1:8b"
    MISTRAL = "mistral:7b"
    GEMMA = "gemma2:9b"
    DEEPSEEK = "deepseek-r1:7b"


class ThemePreference(str, Enum):
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


class DocumentStatus(str, Enum):
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class APIModel(BaseModel):
    """Base model shared by all API-facing schemas."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        json_encoders={datetime: lambda v: v.isoformat()},
    )
