# @file purpose: invoke LLMs and tools via a syscall interface
"""LLM and tool invocation helpers."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ValidationError

from agentic_os import get_registry
from agentic_os.tools import ToolSpec
from browser_use.llm.base import BaseChatModel


class LLMSyscallInterface:
	"""Simple syscall interface for interacting with LLMs and tools."""

	def __init__(self, llm: BaseChatModel, registry: dict[str, ToolSpec] | None = None) -> None:
		self._llm = llm
		self._registry = registry or get_registry()

	async def invoke_llm(self, messages: list[Any], output_model: type[BaseModel] | None = None) -> Any:
		"""Invoke the underlying LLM with the given messages."""
		assert isinstance(messages, list), 'messages must be a list'
		return await self._llm.ainvoke(messages, output_model)

	async def invoke_tool(self, tool_id: str, params: dict[str, Any] | BaseModel | None = None) -> Any:
		"""Invoke a registered tool with validated parameters."""
		if tool_id not in self._registry:
		    raise ValueError(f'unknown tool {tool_id}')

		spec = self._registry[tool_id]
		if spec.func is None:
		    raise ValueError(f'tool {tool_id} is missing callable')

		if spec.input_model is not None:
		    try:
		        if isinstance(params, BaseModel):
		            parsed = params
		        else:
		            parsed = spec.input_model.model_validate(params or {})
		    except ValidationError as exc:
		        raise exc
		else:
		    parsed = params

		result = spec.func(parsed) if parsed is not None else spec.func()
		if hasattr(result, '__await__'):
		    return await result
		return result
