"""Central tool registry used by the orchestrator to discover and invoke tools."""

from typing import Dict, List

from app.tools.base import BaseTool
from app.tools.calculator_tool import CalculatorTool
from app.tools.document_reader_tool import DocumentReaderTool
from app.tools.file_search_tool import FileSearchTool
from app.tools.folder_explorer_tool import FolderExplorerTool
from app.tools.git_reader_tool import GitReaderTool
from app.tools.python_execution_tool import PythonExecutionTool
from app.tools.terminal_tool import TerminalTool


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: Dict[str, BaseTool] = {}
        for tool in (
            CalculatorTool(),
            PythonExecutionTool(),
            FileSearchTool(),
            DocumentReaderTool(),
            FolderExplorerTool(),
            GitReaderTool(),
            TerminalTool(),
        ):
            self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def all_tools(self) -> List[BaseTool]:
        return list(self._tools.values())

    def function_definitions(self) -> List[dict]:
        return [tool.to_function_definition() for tool in self._tools.values()]

    async def invoke(self, name: str, arguments: dict) -> str:
        tool = self.get(name)
        if tool is None:
            return f"Error: tool '{name}' is not registered."
        try:
            return await tool.run(**arguments)
        except TypeError as exc:
            return f"Error: invalid arguments for tool '{name}': {exc}"


_registry: ToolRegistry | None = None


def get_tool_registry() -> ToolRegistry:
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry
