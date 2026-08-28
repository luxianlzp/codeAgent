from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QLabel, QListWidget, QListWidgetItem, QVBoxLayout


class TracePanel(QFrame):
    event_selected = Signal(dict)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("Panel")
        self._events: list[dict] = []

        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self._emit_selected)

        layout = QVBoxLayout(self)
        title = QLabel("Run Trace")
        title.setObjectName("PanelTitle")
        subtitle = QLabel("Live agent events")
        subtitle.setObjectName("Muted")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(8)
        layout.addWidget(self.list_widget, 1)

    def clear(self) -> None:
        self._events.clear()
        self.list_widget.clear()

    def append_event(self, event: dict) -> None:
        self._events.append(event)
        item = QListWidgetItem(_event_summary(event))
        item.setData(256, event)
        self.list_widget.addItem(item)
        self.list_widget.setCurrentRow(self.list_widget.count() - 1)

    def _emit_selected(self, row: int) -> None:
        if 0 <= row < len(self._events):
            self.event_selected.emit(self._events[row])


def _event_summary(event: dict) -> str:
    kind = str(event.get("kind", "event"))
    message = str(event.get("message", ""))
    data = event.get("data") if isinstance(event.get("data"), dict) else {}

    if kind == "model_request":
        step = data.get("step")
        return f"model · calling model · step {step}"
    if kind == "action":
        return f"action · {message}"
    if kind == "tool_call":
        args = data.get("args") if isinstance(data.get("args"), dict) else {}
        return f"tool call · {message} · {_summarize_args(message, args)}"
    if kind == "tool_result":
        ok = data.get("ok")
        tool = data.get("tool")
        status = "ok" if ok else "error"
        return f"tool result · {status} · {tool}"
    if kind == "finish":
        return f"finish · {message}"
    if kind == "error":
        return f"error · {message}"
    if kind == "user_message":
        return f"user · {message}"
    return f"{kind} · {message}"


def _summarize_args(tool_name: str, args: dict) -> str:
    if tool_name == "write_file":
        content = str(args.get("content", ""))
        return f"{args.get('path', '')} ({len(content.splitlines())} lines)"
    if tool_name == "run_command":
        return str(args.get("command", ""))
    if "path" in args:
        return str(args.get("path"))
    return ""
