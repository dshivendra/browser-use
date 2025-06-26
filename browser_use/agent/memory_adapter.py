from __future__ import annotations

import logging

from browser_use.agent.memory import Memory, MemoryConfig

logger = logging.getLogger(__name__)


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
