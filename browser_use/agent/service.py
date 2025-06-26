"""Compatibility layer exposing the :class:`Agent` for importers.

Until the agent implementation is split into smaller modules, this file
simply re-exports :class:`Agent` from ``main`` so existing imports
continue to work.
"""

from .main import Agent

__all__ = ["Agent"]
