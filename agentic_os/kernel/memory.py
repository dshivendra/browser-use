# @file purpose: in-memory working memory for agents
"""Short-term memory storage."""

from __future__ import annotations

from typing import Any, Callable, Dict

from agentic_os.memory import MemoryStore


class InMemoryStore:
	"""Simple in-memory implementation of :class:`MemoryStore`."""

	def __init__(self) -> None:
		self._items: list[Any] = []

	async def store(self, text: str) -> None:
		self._items.append(text)

	async def retrieve(self, limit: int | None = None) -> list[Any]:
		return self._items[-limit:] if limit else list(self._items)

	async def snapshot(self) -> list[Any]:
		return list(self._items)


class MemoryManager:
	"""Manage short term memory for multiple agents."""

	def __init__(self, store_factory: Callable[[], MemoryStore] | None = None) -> None:
		self._store_factory = store_factory or InMemoryStore
		self._stores: Dict[str, MemoryStore] = {}

	def _get_store(self, agent_id: str) -> MemoryStore:
		if agent_id not in self._stores:
			self._stores[agent_id] = self._store_factory()
		return self._stores[agent_id]

	async def remember(self, agent_id: str, text: str) -> None:
		"""Store ``text`` in the agent's working memory."""
		await self._get_store(agent_id).store(text)

	async def recall(self, agent_id: str, limit: int | None = None) -> list[Any]:
		"""Retrieve recent items from the agent's memory."""
		store = self._stores.get(agent_id)
		return await store.retrieve(limit) if store else []

	async def snapshot(self, agent_id: str) -> list[Any]:
		"""Return a snapshot of the agent's memory state."""
		store = self._stores.get(agent_id)
		return await store.snapshot() if store else []
