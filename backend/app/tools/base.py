"""
Base interface every tool must implement.

Tools are self-describing (name + description + JSON schema) so the
orchestrator can present them to the LLM as function-calling candidates,
and so new tools can be registered without touching orchestrator code.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseTool(ABC):
    name: str
    description: str

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Return the JSON schema describing this tool's parameters (OpenAI/Ollama function-calling format)."""

    @abstractmethod
    async def run(self, **kwargs: Any) -> str:
        """Execute the tool and return a string result to feed back to the LLM."""

    def to_function_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.get_schema(),
            },
        }
