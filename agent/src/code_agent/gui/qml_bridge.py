from __future__ import annotations

import json
import os
from pathlib import Path
from uuid import uuid4

from PySide6.QtCore import QObject, Property, QThread, QTimer, Signal, Slot
from PySide6.QtWidgets import QFileDialog, QMessageBox

from code_agent.core import AgentConfig
from code_agent.core.env import load_dotenv_files
from code_agent.gui.widgets.chat_panel import _detail_for_event, _event_data, _label_for_kind, _summary_for_event
from code_agent.gui.worker import AgentWorker
from code_agent.gui.widgets.skill_dialog import SkillDialog
from code_agent.skills import SkillError, SkillStore


class QmlController(QObject):
    eventsChanged = Signal()
    eventsReset = Signal(str)
    eventAdded = Signal(str)
    eventUpdated = Signal(int, str)
    projectsChanged = Signal()
    chatsChanged = Signal()
    workspaceChanged = Signal()
    statusChanged = Signal()
    stepChanged = Signal()
    runningChanged = Signal()
    modelChanged = Signal()
    maxStepsChanged = Signal()
    selectedSkillsChanged = Signal()
    currentChatChanged = Signal()

    def __init__(self) -> None:
        super().__init__()
        load_dotenv_files()
        self._model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self._max_steps = 8
        self._status = "Idle"
        self._step = "—"
        self._running = False
        self._events: list[dict] = []
        self._projects = [self._make_project(self._default_workspace())]
        self._current_project = self._projects[0]["id"]
        self._current_chat = self._projects[0]["chats"][0]["id"]
        self._chat_events: dict[str, list[dict]] = {self._current_chat: []}
        self._stream_event_indexes: dict[tuple[str, int], int] = {}
        self._pending_stream_updates: set[tuple[str, int]] = set()
        self._stream_flush_scheduled = False
        self._last_tool_call_args: dict[tuple[str, str], dict] = {}
        self._selected_skills: list[str] = []
        self._thread: QThread | None = None
        self._worker: AgentWorker | None = None

    @Property(list, notify=eventsChanged)
    def events(self) -> list[dict]:
        return self._events

    @Property(list, notify=projectsChanged)
    def projects(self) -> list[dict]:
        return [{"id": item["id"], "name": item["name"], "path": item["path"]} for item in self._projects]

    @Property(list, notify=chatsChanged)
    def chats(self) -> list[dict]:
        project = self._current_project_item()
        return list(project["chats"]) if project is not None else []

    @Property(str, notify=projectsChanged)
    def currentProjectId(self) -> str:
        return self._current_project

    @Property(str, notify=projectsChanged)
    def currentProjectName(self) -> str:
        project = self._current_project_item()
        return str(project["name"]) if project is not None else "项目"

    @Property(str, notify=currentChatChanged)
    def currentChatTitle(self) -> str:
        current = self._current_chat_item()
        return current["title"] if current else "新对话"

    @Property(str, notify=currentChatChanged)
    def currentChatId(self) -> str:
        return self._current_chat

    @Property(str, notify=workspaceChanged)
    def workspace(self) -> str:
        project = self._current_project_item()
        return str(project["path"]) if project is not None else ""

    @Property(str, notify=statusChanged)
    def status(self) -> str:
        return self._status

    @Property(str, notify=stepChanged)
    def step(self) -> str:
        return self._step

    @Property(bool, notify=runningChanged)
    def running(self) -> bool:
        return self._running

    @Property(str, notify=modelChanged)
    def model(self) -> str:
        return self._model

    @Property(int, notify=maxStepsChanged)
    def maxSteps(self) -> int:
        return self._max_steps

    @Property(list, notify=selectedSkillsChanged)
    def selectedSkills(self) -> list[str]:
        return self._selected_skills

    @Slot(int)
    def setMaxSteps(self, value: int) -> None:
        self._max_steps = max(1, min(30, int(value)))
        self.maxStepsChanged.emit()

    @Slot()
    def chooseWorkspace(self) -> None:
        self.newProject()

    @Slot()
    def pickSkills(self) -> None:
        try:
            skills = SkillStore.default_for_workspace(self.workspace).list()
        except SkillError as exc:
            QMessageBox.warning(None, "Skill error", str(exc))
            return
        if not skills:
            QMessageBox.information(None, "No skills", "当前 Workspace 没有可用 Skill。")
            return
        dialog = SkillDialog(skills, self._selected_skills)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self._selected_skills = dialog.selected_skill_names()
            self.selectedSkillsChanged.emit()

    @Slot()
    def newProject(self) -> None:
        directory = QFileDialog.getExistingDirectory(None, "选择项目文件夹", self.workspace)
        if not directory:
            return
        path = str(Path(directory).resolve())
        existing = next((project for project in self._projects if project["path"] == path), None)
        if existing is None:
            existing = self._make_project(path)
            self._projects = self._projects + [existing]
            self.projectsChanged.emit()

        self._current_project = existing["id"]
        if not existing["chats"]:
            existing["chats"].append(self._make_chat("新对话 1"))
        self._current_chat = existing["chats"][0]["id"]
        self._events = list(self._chat_events.get(self._current_chat, []))
        self.projectsChanged.emit()
        self.workspaceChanged.emit()
        self.chatsChanged.emit()
        self.currentChatChanged.emit()
        self._emit_events_reset()

    @Slot()
    def newChat(self) -> None:
        project = self._current_project_item()
        if project is None:
            return
        chat = self._make_chat(f"新对话 {len(project['chats']) + 1}")
        project["chats"].append(chat)
        self._current_chat = chat["id"]
        self._chat_events[chat["id"]] = []
        self._events = []
        self._clear_stream_indexes_for_chat(self._current_chat)
        self.chatsChanged.emit()
        self.currentChatChanged.emit()
        self._emit_events_reset()

    @Slot(str)
    def selectProject(self, project_id: str) -> None:
        if project_id == self._current_project or self._running:
            return
        project = next((item for item in self._projects if item["id"] == project_id), None)
        if project is None:
            return
        if not project["chats"]:
            project["chats"].append(self._make_chat("新对话 1"))
        self._current_project = project_id
        self._current_chat = project["chats"][0]["id"]
        self._events = list(self._chat_events.get(self._current_chat, []))
        self.projectsChanged.emit()
        self.workspaceChanged.emit()
        self.chatsChanged.emit()
        self.currentChatChanged.emit()
        self._emit_events_reset()

    @Slot(str)
    def selectChat(self, chat_id: str) -> None:
        if chat_id == self._current_chat or self._running:
            return
        if self._chat_by_id(chat_id) is None:
            return
        self._current_chat = chat_id
        self._events = list(self._chat_events.get(chat_id, []))
        self.currentChatChanged.emit()
        self._emit_events_reset()

    @Slot(str)
    def runTask(self, task: str) -> None:
        task = task.strip()
        if not task or self._running:
            return
        if not self.workspace:
            QMessageBox.warning(None, "Missing workspace", "Please choose a workspace.")
            return
        current = self._current_chat_item()
        if current and current["title"].startswith("新对话"):
            current["title"] = " ".join(task.split())[:28]
            self.chatsChanged.emit()
            self.currentChatChanged.emit()
        self._events = []
        self._chat_events[self._current_chat] = []
        self._clear_stream_indexes_for_chat(self._current_chat)
        self._emit_events_reset()
        self._set_running(True)
        self._set_status("Running")
        self._set_step("0")
        config = AgentConfig.from_env(max_steps=self._max_steps)
        self._thread = QThread(self)
        self._worker = AgentWorker(task=task, workspace=self.workspace, config=config, skill_names=self._selected_skills)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.event.connect(self._append_event)
        self._worker.finished.connect(self._finished)
        self._worker.failed.connect(self._failed)
        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._thread.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.finished.connect(self._clear_worker)
        self._thread.start()

    @Slot()
    def stopTask(self) -> None:
        if self._worker is not None and self._thread is not None:
            self._set_status("Stopping")
            self._worker.request_stop()

    @Slot()
    def clearConversation(self) -> None:
        if not self._running:
            self._events = []
            self._chat_events[self._current_chat] = []
            self._clear_stream_indexes_for_chat(self._current_chat)
            self._emit_events_reset()

    def _append_event(self, event: dict) -> None:
        kind = str(event.get("kind", "event"))
        if kind == "step":
            data = event.get("data") if isinstance(event.get("data"), dict) else {}
            self._set_step(str(data.get("step", "—")))
            return
        if kind == "model_delta":
            self._append_model_delta(event)
            return
        if kind == "model_response" and _event_data(event).get("streamed"):
            return
        self._flush_stream_updates()
        if kind == "tool_call":
            data = _event_data(event)
            args = data.get("args") if isinstance(data.get("args"), dict) else {}
            self._last_tool_call_args[(self._current_chat, str(event.get("message", "")))] = args
        item = {
            "kind": kind,
            "label": self._label_for_event(event),
            "summary": self._summary_for_event(event),
            "detail": self._detail_for_event(event),
            "status": self._event_status(event),
            "execution": kind in {"model_request", "model_delta", "action", "tool_call", "tool_result"},
            "terminal": self._is_terminal_event(event),
        }
        self._events = self._events + [item]
        self._chat_events[self._current_chat] = list(self._events)
        self.eventAdded.emit(self._event_to_json(item))

    def _append_model_delta(self, event: dict) -> None:
        data = _event_data(event)
        step = int(data.get("step", 0))
        key = (self._current_chat, step)
        chunk = str(event.get("message", ""))
        if not chunk:
            return

        index = self._stream_event_indexes.get(key)
        events = list(self._events)
        if index is None or index >= len(events) or events[index].get("kind") != "model_delta":
            self._stream_event_indexes[key] = len(events)
            events.append({
                "kind": "model_delta",
                "label": "Thinking",
                "summary": chunk,
                "detail": "",
                "status": "Running",
                "execution": True,
                "terminal": False,
            })
            added = events[-1]
            self._events = events
            self._chat_events[self._current_chat] = list(self._events)
            self.eventAdded.emit(self._event_to_json(added))
            return
        else:
            current = dict(events[index])
            current["summary"] = str(current.get("summary", "")) + chunk
            events[index] = current

        self._events = events
        self._chat_events[self._current_chat] = list(self._events)
        self._pending_stream_updates.add(key)
        self._schedule_stream_flush()

    def _emit_events_reset(self) -> None:
        self.eventsChanged.emit()
        self.eventsReset.emit(json.dumps(self._events, ensure_ascii=False))

    def _schedule_stream_flush(self) -> None:
        if self._stream_flush_scheduled:
            return
        self._stream_flush_scheduled = True
        QTimer.singleShot(60, self._flush_stream_updates)

    def _flush_stream_updates(self) -> None:
        if not self._pending_stream_updates:
            self._stream_flush_scheduled = False
            return
        pending = list(self._pending_stream_updates)
        self._pending_stream_updates.clear()
        self._stream_flush_scheduled = False
        for key in pending:
            index = self._stream_event_indexes.get(key)
            if index is not None and 0 <= index < len(self._events):
                self.eventUpdated.emit(index, self._event_to_json(self._events[index]))

    @Slot()
    def shutdown(self) -> None:
        if self._thread is not None and self._thread.isRunning():
            if self._worker is not None:
                self._worker.request_stop()
            self._thread.quit()
            if not self._thread.wait(3000):
                self._thread.terminate()
                self._thread.wait(1000)

    def _finished(self, result: dict) -> None:
        self._flush_stream_updates()
        self._set_status(str(result.get("status", "finished")))
        self._set_step("Complete")
        self._set_running(False)

    def _failed(self, error: str) -> None:
        self._flush_stream_updates()
        self._set_status("Error")
        self._set_step("Failed")
        self._append_event({"kind": "error", "message": error, "data": {}})
        self._set_running(False)

    def _clear_worker(self) -> None:
        self._thread = None
        self._worker = None

    def _set_status(self, value: str) -> None:
        self._status = value
        self.statusChanged.emit()

    def _set_step(self, value: str) -> None:
        self._step = value
        self.stepChanged.emit()

    def _set_running(self, value: bool) -> None:
        if self._running == value:
            return
        self._running = value
        self.runningChanged.emit()

    def _current_project_item(self) -> dict | None:
        return next((project for project in self._projects if project["id"] == self._current_project), None)

    def _current_chat_item(self) -> dict | None:
        return self._chat_by_id(self._current_chat)

    def _chat_by_id(self, chat_id: str) -> dict | None:
        project = self._current_project_item()
        if project is None:
            return None
        return next((chat for chat in project["chats"] if chat["id"] == chat_id), None)

    def _clear_stream_indexes_for_chat(self, chat_id: str) -> None:
        self._stream_event_indexes = {
            key: index for key, index in self._stream_event_indexes.items() if key[0] != chat_id
        }
        self._pending_stream_updates = {
            key for key in self._pending_stream_updates if key[0] != chat_id
        }

    @staticmethod
    def _event_to_json(event: dict) -> str:
        return json.dumps(event, ensure_ascii=False)

    def _detail_for_event(self, event: dict) -> str:
        data = _event_data(event)
        nested = data.get("data") if isinstance(data.get("data"), dict) else {}
        if event.get("kind") == "tool_result" and data.get("tool") == "run_command":
            args = self._last_tool_call_args.get((self._current_chat, "run_command"), {})
            command = str(args.get("command", "")).strip()
            lines = []
            if command:
                lines.append(f"$ {command}")
                lines.append("")
            if nested.get("stdout"):
                lines.append(str(nested.get("stdout")))
            if nested.get("stderr"):
                if lines:
                    lines.append("")
                lines.append(str(nested.get("stderr")))
            lines.append("")
            lines.append(f"Exit code: {nested.get('exit_code', 'unknown')}")
            return "\n".join(lines)
        return _detail_for_event(event)

    @staticmethod
    def _label_for_event(event: dict) -> str:
        kind = str(event.get("kind", "event"))
        if kind == "user_message":
            return "Task"
        if kind == "model_request":
            return "Thinking"
        if kind == "model_delta":
            return "Thinking"
        if kind == "action":
            return "Agent"
        if kind == "tool_call":
            return "Tool Call"
        if kind == "tool_result":
            return "Tool Result"
        if kind == "finish":
            return "Completed"
        if kind == "error":
            return "Error"
        return _label_for_kind(kind)

    @classmethod
    def _summary_for_event(cls, event: dict) -> str:
        kind = str(event.get("kind", "event"))
        message = str(event.get("message", ""))
        data = _event_data(event)

        if kind == "user_message":
            return message
        if kind == "model_request":
            step = data.get("step")
            return f"Analyzing task{f' · step {step}' if step else ''}"
        if kind == "model_delta":
            return message
        if kind == "action":
            return f"Next step: {message}"
        if kind == "tool_call":
            args = data.get("args") if isinstance(data.get("args"), dict) else {}
            return cls._tool_call_summary(message, args)
        if kind == "tool_result":
            return cls._tool_result_summary(data)
        if kind == "finish":
            return message or "Task completed"
        if kind == "error":
            return message
        return _summary_for_event(event)

    @staticmethod
    def _tool_call_summary(tool: str, args: dict) -> str:
        if tool == "list_files":
            return "Listed files"
        if tool == "read_file":
            return f"Read {Path(str(args.get('path', 'file'))).name}"
        if tool == "write_file":
            return f"Edited {Path(str(args.get('path', 'file'))).name}"
        if tool == "run_command":
            command = str(args.get("command", "")).strip()
            return f"Ran {command}" if command else "Ran command"
        return tool.replace("_", " ").title()

    @staticmethod
    def _tool_result_summary(data: dict) -> str:
        tool = str(data.get("tool", "tool"))
        ok = bool(data.get("ok"))
        nested = data.get("data") if isinstance(data.get("data"), dict) else {}
        suffix = "passed" if ok else "failed"
        if tool == "list_files" and isinstance(nested.get("count"), int):
            return f"Listed {nested['count']} files"
        if tool == "read_file":
            return f"Read file {suffix}"
        if tool == "write_file" and nested.get("path"):
            changed = "changed" if nested.get("changed") else "unchanged"
            return f"Edited {Path(str(nested['path'])).name} · {changed}"
        if tool == "run_command" and "exit_code" in nested:
            return f"Command exited {nested['exit_code']}"
        return f"{tool.replace('_', ' ').title()} {suffix}"

    @staticmethod
    def _is_terminal_event(event: dict) -> bool:
        data = _event_data(event)
        nested = data.get("data") if isinstance(data.get("data"), dict) else {}
        return event.get("kind") == "tool_result" and ("stdout" in nested or "stderr" in nested)

    @staticmethod
    def _make_chat(title: str) -> dict:
        return {"id": uuid4().hex, "title": title}

    @classmethod
    def _make_project(cls, path: str) -> dict:
        resolved = str(Path(path).resolve())
        return {
            "id": uuid4().hex,
            "name": Path(resolved).name or resolved,
            "path": resolved,
            "chats": [cls._make_chat("新对话 1")],
        }

    @staticmethod
    def _event_status(event: dict) -> str:
        kind = event.get("kind")
        if kind == "tool_call":
            return "Running"
        if kind == "tool_result":
            return "Success" if _event_data(event).get("ok") else "Error"
        if kind == "error":
            return "Error"
        return ""

    @staticmethod
    def _default_workspace() -> str:
        current = Path.cwd().resolve()
        for base in (current, *current.parents):
            candidate = base / "examples" / "demo_workspace"
            if candidate.exists():
                return str(candidate)
        return str(current)
