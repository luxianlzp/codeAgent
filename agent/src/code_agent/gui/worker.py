from __future__ import annotations

from pathlib import Path
import traceback

from PySide6.QtCore import QObject, Signal, Slot

from code_agent.core import Agent, AgentConfig
from code_agent.core.events import TraceEvent
from code_agent.core.result import AgentRunResult
from code_agent.llm.openai_client import OpenAICompatibleClient
from code_agent.skills import SkillStore, parse_skill_references
from code_agent.tools import build_default_registry
from code_agent.workspace import Workspace


class AgentWorker(QObject):
    event = Signal(dict)
    finished = Signal(dict)
    failed = Signal(str)

    def __init__(self, task: str, workspace: str, config: AgentConfig, skill_names: list[str] | None = None) -> None:
        super().__init__()
        self._task = task
        self._workspace = workspace
        self._config = config
        self._skill_names = skill_names or []

    @Slot()
    def run(self) -> None:
        try:
            workspace = Workspace(Path(self._workspace))
            tools = build_default_registry(workspace, self._config)
            llm = OpenAICompatibleClient(model=self._config.model, base_url=self._config.base_url)
            agent = Agent(llm=llm, tools=tools, config=self._config)
            skill_store = SkillStore.default_for_workspace(workspace.root)
            skills = skill_store.load(self._skill_names + parse_skill_references(self._task))
            result = agent.run(self._task, on_event=self._emit_event, skills=skills)
            self.finished.emit(result.to_dict())
        except Exception:
            self.failed.emit(traceback.format_exc())

    def _emit_event(self, event: TraceEvent) -> None:
        self.event.emit(event.to_dict())
