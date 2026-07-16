"""Local file search tool — finds files by name pattern within a sandboxed root directory."""

import fnmatch
import os
from pathlib import Path
from typing import Any, Dict, List

from app.config import get_settings
from app.tools.base import BaseTool

MAX_RESULTS = 50


class FileSearchTool(BaseTool):
    name = "file_search"
    description = (
        "Search for files by name pattern (glob syntax, e.g. '*.pdf') within the "
        "user's sandboxed upload directory. Cannot access paths outside the sandbox."
    )

    def __init__(self) -> None:
        self._root = Path(get_settings().upload_dir).resolve()

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Glob pattern to match filenames against, e.g. '*.docx'",
                }
            },
            "required": ["pattern"],
        }

    async def run(self, pattern: str) -> str:
        matches: List[str] = []
        self._root.mkdir(parents=True, exist_ok=True)

        for dirpath, _dirnames, filenames in os.walk(self._root):
            for filename in filenames:
                if fnmatch.fnmatch(filename, pattern):
                    rel_path = Path(dirpath, filename).relative_to(self._root)
                    matches.append(str(rel_path))
                    if len(matches) >= MAX_RESULTS:
                        break
            if len(matches) >= MAX_RESULTS:
                break

        if not matches:
            return f"No files matching pattern '{pattern}' were found."
        return "\n".join(matches)
