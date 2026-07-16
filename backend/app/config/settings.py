"""
Centralized application configuration.

All configuration is sourced from environment variables (see .env.example).
Using pydantic-settings gives us validation, type coercion, and a single
source of truth that every other module imports from instead of
reading os.environ directly.
"""

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---------------- App ----------------
    app_name: str = Field(default="JAYESH Assistant", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_debug: bool = Field(default=True, alias="APP_DEBUG")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    frontend_origin: str = Field(default="http://localhost:5173", alias="FRONTEND_ORIGIN")

    # ---------------- Security ----------------
    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=1440, alias="JWT_EXPIRE_MINUTES")
    rate_limit_per_minute: int = Field(default=60, alias="RATE_LIMIT_PER_MINUTE")

    # ---------------- Firebase ----------------
    firebase_credentials_path: str = Field(..., alias="FIREBASE_CREDENTIALS_PATH")
    firebase_project_id: str = Field(..., alias="FIREBASE_PROJECT_ID")

    # ---------------- MongoDB ----------------
    mongodb_uri: str = Field(default="mongodb://localhost:27017", alias="MONGODB_URI")
    mongodb_db_name: str = Field(default="jayesh_assistant", alias="MONGODB_DB_NAME")

    # ---------------- ChromaDB ----------------
    chroma_host: str = Field(default="localhost", alias="CHROMA_HOST")
    chroma_port: int = Field(default=8001, alias="CHROMA_PORT")
    chroma_collection_documents: str = Field(default="jayesh_documents", alias="CHROMA_COLLECTION_DOCUMENTS")
    chroma_collection_memory: str = Field(default="jayesh_memory", alias="CHROMA_COLLECTION_MEMORY")

    # ---------------- Ollama ----------------
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_embedding_model: str = Field(default="nomic-embed-text", alias="OLLAMA_EMBEDDING_MODEL")
    ollama_default_model: str = Field(default="qwen2.5:7b", alias="OLLAMA_DEFAULT_MODEL")
    ollama_available_models_raw: str = Field(
        default="qwen2.5:7b,llama3.1:8b,mistral:7b,gemma2:9b,deepseek-r1:7b",
        alias="OLLAMA_AVAILABLE_MODELS",
    )
    ollama_request_timeout_seconds: int = Field(default=120, alias="OLLAMA_REQUEST_TIMEOUT_SECONDS")

    # ---------------- Uploads ----------------
    upload_dir: str = Field(default="./app/uploads", alias="UPLOAD_DIR")
    max_upload_size_mb: int = Field(default=25, alias="MAX_UPLOAD_SIZE_MB")
    allowed_upload_extensions_raw: str = Field(
        default=".pdf,.docx,.txt,.png,.jpg,.jpeg", alias="ALLOWED_UPLOAD_EXTENSIONS"
    )

    # ---------------- Logging ----------------
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_json: bool = Field(default=True, alias="LOG_JSON")

    @field_validator("app_env")
    @classmethod
    def validate_app_env(cls, value: str) -> str:
        allowed = {"development", "staging", "production"}
        if value not in allowed:
            raise ValueError(f"APP_ENV must be one of {allowed}, got '{value}'")
        return value

    @property
    def ollama_available_models(self) -> List[str]:
        return [m.strip() for m in self.ollama_available_models_raw.split(",") if m.strip()]

    @property
    def allowed_upload_extensions(self) -> List[str]:
        return [e.strip().lower() for e in self.allowed_upload_extensions_raw.split(",") if e.strip()]

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (loaded once per process)."""
    return Settings()
