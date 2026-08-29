from __future__ import annotations

from collections.abc import Callable

from code_agent.core.actions import AgentAction
from code_agent.core.config import AgentConfig
from code_agent.core.events import TraceEvent
from code_agent.core.messages import Message
from code_agent.core.prompts import SYSTEM_PROMPT
from code_agent.core.result import AgentRunResult
from code_agent.llm.base import LLMClient
from code_agent.skills import Skill, format_skills_for_prompt
from code_agent.tools.registry import ToolRegistry

EventHandler = Callable[[TraceEvent], None]


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

    def run(
        self,
        task: str,
        on_event: EventHandler | None = None,
        skills: list[Skill] | None = None,
    ) -> AgentRunResult:
        events: list[TraceEvent] = []

        def emit(event: TraceEvent) -> None:
            events.append(event)
            if on_event is not None:
                on_event(event)

        emit(TraceEvent("user_message", task))
        active_skills = skills or []
        for skill in active_skills:
            emit(TraceEvent("skill", skill.name, {"path": str(skill.path)}))
        messages = [
            Message("system", self._build_system_prompt(active_skills)),
            Message("user", task),
        ]

        for step in range(1, self._config.max_steps + 1):
            emit(TraceEvent("step", f"Step {step}", {"step": step}))
            emit(TraceEvent("model_request", "Calling model", {"step": step}))
            raw_response = self._complete_model(messages, step, emit)
            emit(TraceEvent("model_response", raw_response, {"step": step, "streamed": True}))
            messages.append(Message("assistant", raw_response))

            action = AgentAction.parse(raw_response)
            emit(TraceEvent("action", action.name, {"args": action.args}))
            if action.is_finish:
                message = action.finish_message
                emit(TraceEvent("finish", message))
                return AgentRunResult("finished", message, events)

            emit(TraceEvent("tool_call", action.name, {"args": action.args}))
            result = self._tools.run(action.name, action.args)
            emit(
                TraceEvent(
                    "tool_result",
                    result.to_observation(),
                    {"tool": action.name, "ok": result.ok, "data": result.data},
                )
            )
            messages.append(Message("user", f"Tool result for {action.name}:\n{result.to_observation()}"))

        message = f"Stopped after max_steps={self._config.max_steps}"
        emit(TraceEvent("error", message, {"max_steps": self._config.max_steps}))
        return AgentRunResult("max_steps", message, events)

    def _complete_model(self, messages: list[Message], step: int, emit: EventHandler) -> str:
        stream_complete = getattr(self._llm, "stream_complete", None)
        if stream_complete is None:
            return self._llm.complete(messages)

        chunks: list[str] = []
        for chunk in stream_complete(messages):
            chunks.append(chunk)
            emit(TraceEvent("model_delta", chunk, {"step": step}))
        return "".join(chunks)

    def _build_system_prompt(self, skills: list[Skill]) -> str:
        parts = [
            SYSTEM_PROMPT,
            "Registered tools:\n" + self._tools.descriptions(),
        ]
        skill_prompt = format_skills_for_prompt(skills)
        if skill_prompt:
            parts.append(skill_prompt)
        return "\n\n".join(parts)
