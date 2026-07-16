"""Unit tests for app.tools.calculator_tool — verifies AST-based safety."""

import pytest

from app.tools.calculator_tool import CalculatorTool


@pytest.fixture
def tool():
    return CalculatorTool()


@pytest.mark.asyncio
async def test_basic_arithmetic(tool):
    assert await tool.run(expression="2 + 3") == "5"


@pytest.mark.asyncio
async def test_operator_precedence(tool):
    assert await tool.run(expression="(4 + 5) * 3 / 2") == "13.5"


@pytest.mark.asyncio
async def test_power_and_modulo(tool):
    assert await tool.run(expression="2 ** 10") == "1024"
    assert await tool.run(expression="17 % 5") == "2"


@pytest.mark.asyncio
async def test_negative_numbers(tool):
    assert await tool.run(expression="-5 + 3") == "-2"


@pytest.mark.asyncio
async def test_rejects_function_calls(tool):
    result = await tool.run(expression="__import__('os').system('echo pwned')")
    assert "Error" in result


@pytest.mark.asyncio
async def test_rejects_name_references(tool):
    result = await tool.run(expression="open('/etc/passwd').read()")
    assert "Error" in result


@pytest.mark.asyncio
async def test_rejects_malformed_expression(tool):
    result = await tool.run(expression="2 +* 3")
    assert "Error" in result


def test_schema_shape(tool):
    schema = tool.get_schema()
    assert schema["required"] == ["expression"]
    assert "expression" in schema["properties"]
