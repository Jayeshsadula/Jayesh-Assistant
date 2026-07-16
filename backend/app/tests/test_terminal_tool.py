"""Unit tests for app.tools.terminal_tool — verifies the sandbox rejects unsafe input."""

import pytest

from app.tools.terminal_tool import TerminalTool


@pytest.fixture
def tool():
    return TerminalTool()


@pytest.mark.asyncio
async def test_allows_whitelisted_command(tool):
    result = await tool.run(command="echo hello")
    assert "hello" in result


@pytest.mark.asyncio
async def test_rejects_pipe(tool):
    result = await tool.run(command="ls | rm -rf /")
    assert "rejected" in result.lower()


@pytest.mark.asyncio
async def test_rejects_redirect(tool):
    result = await tool.run(command="echo hi > /etc/passwd")
    assert "rejected" in result.lower()


@pytest.mark.asyncio
async def test_rejects_command_chaining(tool):
    result = await tool.run(command="ls; rm -rf /")
    assert "rejected" in result.lower()


@pytest.mark.asyncio
async def test_rejects_non_whitelisted_binary(tool):
    result = await tool.run(command="curl http://evil.example.com")
    assert "rejected" in result.lower()


@pytest.mark.asyncio
async def test_rejects_empty_command(tool):
    result = await tool.run(command="   ")
    assert "empty" in result.lower()
