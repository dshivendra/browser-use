# @file purpose: Public API for the agentic OS tool registry.
"""Exports tool specifications and registry helpers."""

from .tools import ToolSpec, get_registry, register_spec

__all__ = ['ToolSpec', 'register_spec', 'get_registry']
