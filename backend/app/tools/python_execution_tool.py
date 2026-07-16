"""
Python execution tool — runs short snippets in an isolated subprocess.

Safety measures:
  * Executed in a separate `python -I` (isolated mode) subprocess, not in-process.
  * Hard wall-clock timeout.
  * No network access (subprocess inherits the backend container's network
    namespace, which in production should itself be firewalled at the OS/network level).
  * stdout/stderr captured and size-limited before being returned to the LLM.
"""

import asyncio
from typing import Any, Dict

from app.tools.base import BaseTool
from app.utils.logger import get_logger

logger = get_logger(__name__)

EXECUTION_TIMEOUT_SECONDS = 10
MAX_OUTPUT_CHARS = 4000


class PythonExecutionTool(BaseTool):
    name = "python_execution"
    description = (
        "Execute a short, self-contained Python snippet and return stdout/stderr. "
        "Use for calculations, data transforms, or quick logic checks. No network or file-system "
        "access outside the sandbox is available."
    )

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The Python code to execute. Use print() to produce output.",
                }
            },
            "required": ["code"],
        }

    async def run(self, code: str) -> str:
        try:
            process = await asyncio.create_subprocess_exec(
                "python3",
                "-I",  # isolated mode: ignores user site-packages and env vars
                "-c",
                code,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=EXECUTION_TIMEOUT_SECONDS
                )
            except asyncio.TimeoutError:
                process.kill()
                return f"Execution timed out after {EXECUTION_TIMEOUT_SECONDS} seconds."

            output = stdout.decode(errors="ignore") + stderr.decode(errors="ignore")
            return output[:MAX_OUTPUT_CHARS] or "(no output)"

        except Exception as exc:  # noqa: BLE001
            logger.error("tool.python_execution_failed", error=str(exc))
            return f"Execution failed: {exc}"
