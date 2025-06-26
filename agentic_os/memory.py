from __future__ import annotations

from typing import Protocol, Any, runtime_checkable


@runtime_checkable
class MemoryStore(Protocol):
    async def store(self, text: str) -> None: ...

    async def retrieve(self, limit: int | None = None) -> list[Any]: ...

    async def snapshot(self) -> list[Any]: ...
