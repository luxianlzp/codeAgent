from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from code_agent.core.events import TraceEvent

RunStatus = Literal["finished", "max_steps", "error"]


@dataclass(frozen=True)
class AgentRunResult:
    status: RunStatus
    final_message: str
    events: list[TraceEvent]

    @property
    def ok(self) -> bool:
        return self.status == "finished"

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "final_message": self.final_message,
            "events": [event.to_dict() for event in self.events],
        }
