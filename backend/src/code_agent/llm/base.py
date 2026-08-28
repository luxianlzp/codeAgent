from __future__ import annotations

from typing import Protocol

from code_agent.core.messages import Message


class LLMClient(Protocol):
    def complete(self, messages: list[Message]) -> str:
        """Return the assistant message content for the given conversation."""

    def stream_complete(self, messages: list[Message]):
        """Yield assistant message content chunks for the given conversation."""
