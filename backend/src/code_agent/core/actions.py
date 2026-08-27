from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any


@dataclass(frozen=True)
class AgentAction:
    name: str
    args: dict[str, Any] = field(default_factory=dict)

    @property
    def is_finish(self) -> bool:
        return self.name == "finish"

    @property
    def finish_message(self) -> str:
        return str(self.args.get("message", "Done."))

    @classmethod
    def parse(cls, raw_response: str) -> "AgentAction":
        try:
            parsed = json.loads(raw_response)
        except json.JSONDecodeError as exc:
            return cls(
                "finish",
                {
                    "message": (
                        "Model response was not valid JSON, so the agent stopped. "
                        f"Parse error: {exc}"
                    )
                },
            )

        if not isinstance(parsed, dict):
            return cls("finish", {"message": "Model response was not a JSON object."})
        action = parsed.get("action")
        if not isinstance(action, str) or not action:
            return cls("finish", {"message": "Model response did not include action."})
        args = parsed.get("args", {})
        if not isinstance(args, dict):
            args = {}
        return cls(action, args)
