# @file purpose: persistent storage for agent data
"""Disk backed storage manager."""

from __future__ import annotations

from pathlib import Path

import aiofiles


class StorageManager:
	"""Persist agent data to disk with basic security checks."""

	def __init__(self, base_dir: str | Path) -> None:
		self.base_dir = Path(base_dir)
		self.base_dir.mkdir(parents=True, exist_ok=True)

	def _resolve_path(self, agent_id: str, filename: str) -> Path:
		agent_dir = self.base_dir / agent_id
		agent_dir.mkdir(parents=True, exist_ok=True)
		path = (agent_dir / filename).resolve()
		if not str(path).startswith(str(self.base_dir.resolve())):
			raise ValueError('invalid file path outside storage directory')
		return path

	async def write_text(self, agent_id: str, filename: str, text: str) -> None:
		path = self._resolve_path(agent_id, filename)
		async with aiofiles.open(path, 'w') as f:
			await f.write(text)

	async def read_text(self, agent_id: str, filename: str) -> str:
		path = self._resolve_path(agent_id, filename)
		async with aiofiles.open(path, 'r') as f:
			return await f.read()

	async def write_bytes(self, agent_id: str, filename: str, data: bytes) -> None:
		path = self._resolve_path(agent_id, filename)
		async with aiofiles.open(path, 'wb') as f:
			await f.write(data)

	async def read_bytes(self, agent_id: str, filename: str) -> bytes:
		path = self._resolve_path(agent_id, filename)
		async with aiofiles.open(path, 'rb') as f:
			return await f.read()
