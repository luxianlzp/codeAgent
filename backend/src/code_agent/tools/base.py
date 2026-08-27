from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class ToolResult:
    ok: bool
    output: str
    data: dict[str, Any] | None = None

    def to_observation(self) -> str:
        status = "ok" if self.ok else "error"
        return f"{status}: {self.output}"


class Tool(Protocol):
    name: str
    description: str

    def run(self, args: dict[str, Any]) -> ToolResult:
        """Run the tool with JSON-like arguments."""
