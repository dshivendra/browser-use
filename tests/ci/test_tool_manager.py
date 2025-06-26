from pydantic import BaseModel
from pytest import raises

from agentic_os.kernel.tool import ToolManager
from agentic_os.tools import ToolSpec


class Params(BaseModel):
	value: int


async def add_one(params: Params) -> int:
	return params.value + 1


async def test_register_and_execute():
	spec = ToolSpec("adder", "add one", Params, Params, add_one)
	mgr = ToolManager([spec])

	result = await mgr.execute("adder", {"value": 1})
	assert result == 2


async def test_conflict_detection():
	spec1 = ToolSpec("t", "desc", Params, Params, add_one)
	mgr = ToolManager([spec1])

	async def other(params: Params) -> int:
		return params.value

	spec2 = ToolSpec("t", "desc", Params, Params, other)
	with raises(ValueError):
		mgr.register(spec2)
