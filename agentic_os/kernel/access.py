from __future__ import annotations

from typing import Iterable, Dict, Set

import logging


class AccessManager:
	"""Simple permission manager that logs agent access events."""

	def __init__(self, permissions: Dict[str, Iterable[str]] | None = None, logger: logging.Logger | None = None) -> None:
		self._perms: Dict[str, Set[str]] = {k: set(v) for k, v in (permissions or {}).items()}
		self._logger = logger or logging.getLogger(__name__)

	def grant(self, agent_id: str, tool_id: str) -> None:
		"""Allow ``agent_id`` to use ``tool_id``."""
		self._perms.setdefault(agent_id, set()).add(tool_id)
		self._logger.info("grant %s -> %s", agent_id, tool_id)

	def revoke(self, agent_id: str, tool_id: str) -> None:
		"""Revoke ``tool_id`` for ``agent_id``."""
		if agent_id in self._perms:
			self._perms[agent_id].discard(tool_id)
		self._logger.info("revoke %s -> %s", agent_id, tool_id)

	def is_allowed(self, agent_id: str, tool_id: str) -> bool:
		"""Return whether ``agent_id`` may access ``tool_id``."""
		allowed = tool_id in self._perms.get(agent_id, set())
		self._logger.info("access %s -> %s : %s", agent_id, tool_id, allowed)
		return allowed

	def ensure_allowed(self, agent_id: str, tool_id: str) -> None:
		"""Raise :class:`PermissionError` if ``agent_id`` lacks permission."""
		if not self.is_allowed(agent_id, tool_id):
			raise PermissionError(f"{agent_id} may not access {tool_id}")
