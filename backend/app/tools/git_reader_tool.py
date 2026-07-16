"""
Git repository reader tool.

Read-only: only a fixed allow-list of git subcommands can be run
(log, show, diff, status, branch), and only against repositories that live
inside the sandboxed upload root. No push/commit/checkout/reset — this tool
inspects history, it never mutates it.
"""

import asyncio
from pathlib import Path
from typing import Any, Dict

from app.config import get_settings
from app.tools.base import BaseTool
from app.utils.exceptions import ForbiddenError

ALLOWED_SUBCOMMANDS = {"log", "show", "diff", "status", "branch"}
EXECUTION_TIMEOUT_SECONDS = 10
MAX_OUTPUT_CHARS = 4000


class GitReaderTool(BaseTool):
    name = "git_repository_reader"
    description = (
        "Run a read-only git command (log, show, diff, status, branch) against a repository "
        "inside the user's sandboxed upload directory. Cannot modify the repository."
    )

    def __init__(self) -> None:
        self._root = Path(get_settings().upload_dir).resolve()

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "repo_relative_path": {
                    "type": "string",
                    "description": "Path to the git repo, relative to the sandbox root.",
                },
                "subcommand": {
                    "type": "string",
                    "enum": sorted(ALLOWED_SUBCOMMANDS),
                    "description": "Read-only git subcommand to run.",
                },
                "args": {
                    "type": "string",
                    "description": "Extra arguments to pass, e.g. '-n 5' for log.",
                    "default": "",
                },
            },
            "required": ["repo_relative_path", "subcommand"],
        }

    async def run(self, repo_relative_path: str, subcommand: str, args: str = "") -> str:
        if subcommand not in ALLOWED_SUBCOMMANDS:
            return f"Subcommand '{subcommand}' is not allowed. Allowed: {sorted(ALLOWED_SUBCOMMANDS)}"

        repo_path = (self._root / repo_relative_path).resolve()
        if self._root not in repo_path.parents and repo_path != self._root:
            raise ForbiddenError("Access outside the sandboxed directory is not allowed.")
        if not (repo_path / ".git").exists():
            return f"'{repo_relative_path}' is not a git repository."

        command = ["git", "-C", str(repo_path), subcommand, *args.split()]

        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=EXECUTION_TIMEOUT_SECONDS)
        except asyncio.TimeoutError:
            process.kill()
            return "Git command timed out."

        output = stdout.decode(errors="ignore") + stderr.decode(errors="ignore")
        return output[:MAX_OUTPUT_CHARS] or "(no output)"
