# @file purpose: register and execute tool specifications
"""Tool registry and execution helpers."""

from __future__ import annotations

from typing import Any, Iterable, Dict

from pydantic import BaseModel

from agentic_os.tools import ToolSpec


class ToolManager:
	"""Manage loading and execution of registered tools."""

	def __init__(self, specs: Iterable[ToolSpec] | None = None) -> None:
		self._registry: Dict[str, ToolSpec] = {}
		if specs:
			for spec in specs:
				self.register(spec)

	def register(self, spec: ToolSpec) -> None:
		"""Register a :class:`ToolSpec`, checking for conflicts."""
		if spec.id in self._registry:
			existing = self._registry[spec.id]
			if existing != spec:
				raise ValueError(f'conflicting spec for {spec.id}')
			return
		self._registry[spec.id] = spec

	def load_from(self, registry: Dict[str, ToolSpec]) -> None:
		"""Load multiple specs from an existing registry."""
		for spec in registry.values():
			self.register(spec)

	def get(self, tool_id: str) -> ToolSpec:
		"""Return the spec for ``tool_id``."""
		return self._registry[tool_id]

	async def execute(self, tool_id: str, params: dict[str, Any] | BaseModel | None = None) -> Any:
		"""Validate ``params`` using the tool's model and run it."""
		spec = self.get(tool_id)
		if spec.func is None:
			raise ValueError(f'tool {tool_id} has no callable')

		if spec.input_model is not None:
			parsed = params if isinstance(params, BaseModel) else spec.input_model.model_validate(params or {})
		else:
			parsed = params

		result = spec.func(parsed) if parsed is not None else spec.func()
		if hasattr(result, '__await__'):
			return await result
		return result
