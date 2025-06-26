import browser_use.tools  # register specs
from agentic_os import get_registry


def test_tool_spec_functions_registered():
	registry = get_registry()
	assert registry
	assert all(callable(spec.func) for spec in registry.values())
