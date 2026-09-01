from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class AgentConfig:
    model: str = "gpt-4o-mini"
    base_url: str = "https://api.openai.com/v1"
    max_steps: int = 8
    command_timeout_seconds: int = 30
    model_timeout_seconds: int = 60

    @classmethod
    def from_env(cls, max_steps: int | None = None) -> "AgentConfig":
        return cls(
            model=os.getenv("OPENAI_MODEL", cls.model),
            base_url=os.getenv("OPENAI_BASE_URL", cls.base_url),
            max_steps=max_steps or int(os.getenv("CODE_AGENT_MAX_STEPS", "8")),
            command_timeout_seconds=int(os.getenv("CODE_AGENT_COMMAND_TIMEOUT", "30")),
            model_timeout_seconds=int(os.getenv("CODE_AGENT_MODEL_TIMEOUT", "60")),
        )
