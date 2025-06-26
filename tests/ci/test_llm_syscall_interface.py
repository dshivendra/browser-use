from pydantic import BaseModel
from pytest import raises
from unittest.mock import AsyncMock

from agentic_os.kernel.syscall import LLMSyscallInterface
from agentic_os.tools import ToolSpec


class SimpleParams(BaseModel):
	value: int


async def test_invoke_llm_dispatch():
	mock_llm = AsyncMock()
	mock_llm.ainvoke.return_value = 'ok'
	iface = LLMSyscallInterface(mock_llm, {})

	result = await iface.invoke_llm(['hello'])

	assert result == 'ok'
	mock_llm.ainvoke.assert_awaited_once_with(['hello'], None)


async def test_invoke_tool_dispatch():
	async def tool(params: SimpleParams) -> int:
		return params.value + 1

	spec = ToolSpec('adder', 'add', SimpleParams, SimpleParams, tool)
	iface = LLMSyscallInterface(AsyncMock(), {'adder': spec})

	result = await iface.invoke_tool('adder', {'value': 1})

	assert result == 2


async def test_invoke_tool_unknown():
	iface = LLMSyscallInterface(AsyncMock(), {})
	with raises(ValueError):
		await iface.invoke_tool('missing', {})


async def test_invoke_tool_validation_error():
	async def tool(params: SimpleParams) -> int:
		return params.value

	spec = ToolSpec('echo', 'echo', SimpleParams, SimpleParams, tool)
	iface = LLMSyscallInterface(AsyncMock(), {'echo': spec})

	with raises(Exception):
		await iface.invoke_tool('echo', {'wrong': 1})
