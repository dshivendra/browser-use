# @file purpose: Adapters for enabling memory features in the agent.
"""In-memory storage and helper routines for agent memory management."""

from __future__ import annotations

import logging
import time

from pydantic import BaseModel, Field

from browser_use.agent.memory import Memory, MemoryConfig

logger = logging.getLogger(__name__)


class MemoryEntry(BaseModel):
    """A single memory item stored in :class:`BrowserMemory`."""

    text: str
    timestamp: float = Field(default_factory=lambda: time.time())


class BrowserMemory:
    """Simple in-memory storage for text snippets."""

    def __init__(self) -> None:
        self._entries: list[MemoryEntry] = []
        self.logger = logger.getChild('BrowserMemory')

    async def store(self, text: str) -> None:
        """Store a new memory entry."""
        self._entries.append(MemoryEntry(text=text))

    async def retrieve(self, limit: int | None = None) -> list[MemoryEntry]:
        """Retrieve the most recent memory entries."""
        if limit is None:
            return list(self._entries)
        return self._entries[-limit:]

    async def snapshot(self) -> list[MemoryEntry]:
        """Return a copy of all stored memories."""
        return list(self._entries)


def initialize_memory(agent) -> None:
    if agent.enable_memory:
        try:
            agent.memory = Memory(
                message_manager=agent._message_manager,
                llm=agent.llm,
                config=agent.memory_config,
            )
        except ImportError:
            agent.logger.warning(
                '⚠️ Agent(enable_memory=True) is set but missing some required packages, install and re-run to use memory features: pip install browser-use[memory]'
            )
            agent.memory = None
            agent.enable_memory = False
    else:
        agent.memory = None


def maybe_create_procedural_memory(agent) -> None:
    if (
        agent.enable_memory
        and agent.memory
        and agent.state.n_steps % agent.memory.config.memory_interval == 0
    ):
        agent.memory.create_procedural_memory(agent.state.n_steps)
