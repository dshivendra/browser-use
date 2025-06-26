# @file purpose: manage LLM context windows
"""Context window management utilities."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from browser_use.llm.messages import BaseMessage


class ContextSnapshot(BaseModel):
	"""Serialized snapshot of a context window."""

	messages: list[BaseMessage] = Field(default_factory=list)
	"""Messages currently stored in the context."""

	current_tokens: int
	"""Approximate number of tokens in ``messages``."""

	max_tokens: int
	"""Maximum allowed tokens for the context window."""

	model_config = ConfigDict(arbitrary_types_allowed=True)


class ContextManager:
	"""Manage a rolling context window for LLM tasks."""

	def __init__(self, max_tokens: int = 4096) -> None:
		self.max_tokens = max_tokens
		self._messages: list[BaseMessage] = []
		self._current_tokens = 0

	def _count_tokens(self, message: BaseMessage) -> int:
		"""Very rough token estimate based on whitespace splitting."""
		text = getattr(message, 'text', str(message))
		return len(str(text).split())

	def add_message(self, message: BaseMessage) -> None:
		"""Add ``message`` to the context, trimming old messages if needed."""
		self._messages.append(message)
		self._current_tokens += self._count_tokens(message)
		self._trim_messages()

	def _trim_messages(self) -> None:
		"""Ensure token count stays within ``max_tokens``."""
		while self._messages and self._current_tokens > self.max_tokens:
			removed = self._messages.pop(0)
			self._current_tokens -= self._count_tokens(removed)

	def get_messages(self) -> list[BaseMessage]:
		"""Return a copy of the current message list."""
		return list(self._messages)

	def snapshot(self) -> ContextSnapshot:
		"""Return a snapshot representing the current context."""
		return ContextSnapshot(
			messages=self.get_messages(),
			current_tokens=self._current_tokens,
			max_tokens=self.max_tokens,
		)

	def restore(self, snapshot: ContextSnapshot) -> None:
		"""Restore context state from ``snapshot``."""
		self.max_tokens = snapshot.max_tokens
		self._messages = list(snapshot.messages)
		self._current_tokens = snapshot.current_tokens
