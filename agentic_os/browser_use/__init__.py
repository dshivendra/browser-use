"""Compatibility wrapper for the ``browser_use`` package.

This module exposes the public API of :mod:`browser_use` under
``agentic_os.browser_use`` so existing code can migrate seamlessly.
"""

import browser_use
from browser_use import *  # noqa: F401,F403
from browser_use.agent.planning import BrowserPlanner, Plan, PlannerContext
from browser_use.agent.memory_adapter import (
    BrowserMemory,
    initialize_memory,
    maybe_create_procedural_memory,
)

__all__ = [
    *browser_use.__all__,  # type: ignore[name-defined]
    "BrowserPlanner",
    "Plan",
    "PlannerContext",
    "BrowserMemory",
    "initialize_memory",
    "maybe_create_procedural_memory",
]
