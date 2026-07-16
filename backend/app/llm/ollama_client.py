"""
Thin async wrapper around the Ollama HTTP API.

This is the single point of contact with Ollama. Every other module
(orchestrator, RAG embedder, tools) should go through this client rather
than calling `httpx` directly, so retry/timeout/error-handling behavior
stays consistent.
"""

from typing import AsyncGenerator, List

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import get_settings
from app.utils.exceptions import UpstreamServiceError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class OllamaClient:
    def __init__(self) -> None:
        settings = get_settings()
        self._base_url = settings.ollama_base_url.rstrip("/")
        self._timeout = settings.ollama_request_timeout_seconds
        self._embedding_model = settings.ollama_embedding_model

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=1, max=8),
        retry=retry_if_exception_type(httpx.TransportError),
    )
    async def list_models(self) -> List[str]:
        async with httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout) as client:
            try:
                resp = await client.get("/api/tags")
                resp.raise_for_status()
            except httpx.HTTPError as exc:
                logger.error("ollama.list_models_failed", error=str(exc))
                raise UpstreamServiceError("Could not reach Ollama to list models.") from exc

            data = resp.json()
            return [m["name"] for m in data.get("models", [])]

    async def stream_chat(
        self,
        model: str,
        messages: List[dict],
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        """Yield response tokens as they arrive from Ollama's /api/chat endpoint."""
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "options": {"temperature": temperature},
        }

        try:
            async with httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout) as client:
                async with client.stream("POST", "/api/chat", json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        import json as _json

                        chunk = _json.loads(line)
                        token = chunk.get("message", {}).get("content", "")
                        if token:
                            yield token
                        if chunk.get("done"):
                            break
        except httpx.HTTPError as exc:
            logger.error("ollama.stream_chat_failed", model=model, error=str(exc))
            raise UpstreamServiceError(
                f"Could not reach Ollama model '{model}'. Ensure it is pulled and Ollama is running."
            ) from exc

    async def chat(
        self,
        model: str,
        messages: List[dict],
        tools: List[dict] | None = None,
        temperature: float = 0.3,
    ) -> dict:
        """Non-streaming chat completion, optionally with function/tool-calling.

        Returns the raw `message` dict from Ollama, which may contain a
        `tool_calls` field if the model decided to invoke a tool.
        """
        payload: dict = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if tools:
            payload["tools"] = tools

        async with httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout) as client:
            try:
                resp = await client.post("/api/chat", json=payload)
                resp.raise_for_status()
            except httpx.HTTPError as exc:
                logger.error("ollama.chat_failed", model=model, error=str(exc))
                raise UpstreamServiceError(
                    f"Could not reach Ollama model '{model}'. Ensure it is pulled and Ollama is running."
                ) from exc

            data = resp.json()
            return data.get("message", {})

    async def embed(self, text: str) -> List[float]:
        payload = {"model": self._embedding_model, "prompt": text}
        async with httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout) as client:
            try:
                resp = await client.post("/api/embeddings", json=payload)
                resp.raise_for_status()
            except httpx.HTTPError as exc:
                logger.error("ollama.embed_failed", error=str(exc))
                raise UpstreamServiceError("Could not reach Ollama to generate embeddings.") from exc

            data = resp.json()
            return data.get("embedding", [])


_client: OllamaClient | None = None


def get_ollama_client() -> OllamaClient:
    global _client
    if _client is None:
        _client = OllamaClient()
    return _client
