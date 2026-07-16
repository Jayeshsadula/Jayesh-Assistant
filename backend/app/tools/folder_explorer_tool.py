"""Folder explorer tool — lists contents of a directory within the sandboxed upload root."""

from pathlib import Path
from typing import Any, Dict

from app.config import get_settings
from app.tools.base import BaseTool
from app.utils.exceptions import ForbiddenError


class FolderExplorerTool(BaseTool):
    name = "folder_explorer"
    description = (
        "List files and subfolders inside a directory within the user's sandboxed "
        "upload area. Path must be relative (e.g. 'reports/2024')."
    )

    def __init__(self) -> None:
        self._root = Path(get_settings().upload_dir).resolve()

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "relative_path": {
                    "type": "string",
                    "description": "Relative path from the sandbox root. Use '.' for the root itself.",
                }
            },
            "required": ["relative_path"],
        }

    def _resolve_safe_path(self, relative_path: str) -> Path:
        candidate = (self._root / relative_path).resolve()
        if self._root not in candidate.parents and candidate != self._root:
            raise ForbiddenError("Access outside the sandboxed directory is not allowed.")
        return candidate

    async def run(self, relative_path: str) -> str:
        self._root.mkdir(parents=True, exist_ok=True)
        target = self._resolve_safe_path(relative_path)

        if not target.exists():
            return f"Path '{relative_path}' does not exist."
        if not target.is_dir():
            return f"Path '{relative_path}' is not a directory."

        entries = sorted(target.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        lines = [f"{'[dir] ' if e.is_dir() else '[file]'} {e.name}" for e in entries]
        return "\n".join(lines) if lines else "(empty directory)"
