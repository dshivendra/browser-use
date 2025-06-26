# @file purpose: cooperative scheduler for agent generators
"""Run multiple async agents in priority order."""

from __future__ import annotations

import heapq
from collections.abc import AsyncGenerator
from typing import Any


class AgentScheduler:
	"""Simple cooperative scheduler for agent async generators."""

	def __init__(self, strategy: str = 'fifo') -> None:
		if strategy not in {'fifo', 'round_robin'}:
			raise ValueError('strategy must be "fifo" or "round_robin"')
		self.strategy = strategy
		self._agents: dict[str, AsyncGenerator[Any, None]] = {}
		self._queue: list[tuple[int, int, str]] = []
		self._counter = 0

	def register_agent(self, agent_id: str, generator: AsyncGenerator[Any, None], priority: int = 0) -> None:
		"""Register an async generator representing an agent."""
		if agent_id in self._agents:
			raise ValueError(f'agent {agent_id} already registered')
		self._agents[agent_id] = generator
		heapq.heappush(self._queue, (-priority, self._counter, agent_id))
		self._counter += 1

	@property
	def has_agents(self) -> bool:
		return bool(self._queue)

	async def step(self) -> tuple[str, Any] | None:
		"""Run a single scheduling step and return the yielded result."""
		if not self._queue:
			return None

		if self.strategy == 'fifo':
			priority, count, agent_id = self._queue[0]
		else:
			priority, count, agent_id = heapq.heappop(self._queue)

		gen = self._agents[agent_id]
		try:
			result = await anext(gen)
		except StopAsyncIteration:
			if self.strategy == 'fifo':
				heapq.heappop(self._queue)
			del self._agents[agent_id]
			return await self.step() if self._queue else None
		else:
			if self.strategy == 'round_robin':
				heapq.heappush(self._queue, (priority, self._counter, agent_id))
				self._counter += 1
			return agent_id, result

	async def run(self) -> AsyncGenerator[tuple[str, Any], None]:
		"""Yield results from agents according to the selected strategy."""
		while self._queue:
			step = await self.step()
			if step is not None:
				yield step
