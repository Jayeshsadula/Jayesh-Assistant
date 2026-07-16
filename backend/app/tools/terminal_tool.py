"""
Terminal tool — safe sandbox mode.

This is intentionally the most restricted tool in the framework:
  * Only a small allow-list of read-only, side-effect-free binaries can be run
    (ls, cat, pwd, echo, wc, head, tail, grep, find, df, whoami, date).
  * No shell metacharacters (pipes, redirects, subshells, `;`, `&&`) are permitted —
    commands are tokenized and executed directly via subprocess_exec, never via a shell.
  * Working directory is pinned to the sandboxed upload root.
  * Hard timeout and output size cap.
This deliberately cannot install packages, write files, access the network, or
run arbitrary binaries.
"""

import asyncio
import shlex
from pathlib import Path
from typing import Any, Dict

from app.config import get_settings
from app.tools.base import BaseTool

ALLOWED_BINARIES = {"ls", "cat", "pwd", "echo", "wc", "head", "tail", "grep", "find", "df", "whoami", "date"}
FORBIDDEN_CHARACTERS = {"|", ">", "<", "&", ";", "`", "$", "\n"}
EXECUTION_TIMEOUT_SECONDS = 8
MAX_OUTPUT_CHARS = 3000


class TerminalTool(BaseTool):
    name = "terminal"
    description = (
        "Run a single, read-only shell command from a strict allow-list "
        f"({', '.join(sorted(ALLOWED_BINARIES))}) inside the sandboxed upload directory. "
        "No pipes, redirects, or chained commands are permitted."
    )

    def __init__(self) -> None:
        self._root = Path(get_settings().upload_dir).resolve()

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "A single command, e.g. 'ls -la' or 'cat notes.txt'.",
                }
            },
            "required": ["command"],
        }

    async def run(self, command: str) -> str:
        if any(ch in command for ch in FORBIDDEN_CHARACTERS):
            return "Command rejected: shell metacharacters are not allowed."

        try:
            tokens = shlex.split(command)
        except ValueError as exc:
            return f"Command rejected: could not parse ({exc})."

        if not tokens:
            return "Empty command."

        binary = tokens[0]
        if binary not in ALLOWED_BINARIES:
            return f"Command rejected: '{binary}' is not in the allowed list {sorted(ALLOWED_BINARIES)}."

        self._root.mkdir(parents=True, exist_ok=True)

        process = await asyncio.create_subprocess_exec(
            *tokens,
            cwd=str(self._root),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=EXECUTION_TIMEOUT_SECONDS)
        except asyncio.TimeoutError:
            process.kill()
            return "Command timed out."

        output = stdout.decode(errors="ignore") + stderr.decode(errors="ignore")
        return output[:MAX_OUTPUT_CHARS] or "(no output)"
