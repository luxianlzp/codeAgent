from __future__ import annotations

import json
from typing import Any

from code_agent.core.config import AgentConfig
from code_agent.core.events import TraceEvent
from code_agent.core.messages import Message
from code_agent.core.prompts import SYSTEM_PROMPT
from code_agent.llm.base import LLMClient
from code_agent.tools.registry import ToolRegistry


class Agent:
    def __init__(
        self,
        llm: LLMClient,
        tools: ToolRegistry,
        config: AgentConfig,
    ) -> None:
        self._llm = llm
        self._tools = tools
        self._config = config

    def run(self, task: str) -> list[TraceEvent]:
        events: list[TraceEvent] = [TraceEvent("user_message", task)]
        messages = [
            Message("system", SYSTEM_PROMPT + "\n\nRegistered tools:\n" + self._tools.descriptions()),
            Message("user", task),
        ]

        for step in range(1, self._config.max_steps + 1):
            events.append(TraceEvent("step", f"Step {step}"))
            raw_response = self._llm.complete(messages)
            events.append(TraceEvent("model_response", raw_response))
            messages.append(Message("assistant", raw_response))

            action = self._parse_action(raw_response)
            if action["action"] == "finish":
                message = str(action.get("args", {}).get("message", "Done."))
                events.append(TraceEvent("finish", message))
                return events

            tool_name = action["action"]
            tool_args = action.get("args", {})
            events.append(TraceEvent("tool_call", tool_name, {"args": tool_args}))
            result = self._tools.run(tool_name, tool_args)
            events.append(
                TraceEvent(
                    "tool_result",
                    result.to_observation(),
                    {"tool": tool_name, "ok": result.ok, "data": result.data},
                )
            )
            messages.append(Message("user", f"Tool result for {tool_name}:\n{result.to_observation()}"))

        events.append(TraceEvent("error", f"Stopped after max_steps={self._config.max_steps}"))
        return events

    def _parse_action(self, raw_response: str) -> dict[str, Any]:
        try:
            parsed = json.loads(raw_response)
        except json.JSONDecodeError as exc:
            return {
                "action": "finish",
                "args": {
                    "message": (
                        "Model response was not valid JSON, so the agent stopped. "
                        f"Parse error: {exc}"
                    )
                },
            }

        if not isinstance(parsed, dict):
            return {"action": "finish", "args": {"message": "Model response was not a JSON object."}}
        if "action" not in parsed:
            return {"action": "finish", "args": {"message": "Model response did not include action."}}
        if "args" not in parsed or not isinstance(parsed["args"], dict):
            parsed["args"] = {}
        return parsed
