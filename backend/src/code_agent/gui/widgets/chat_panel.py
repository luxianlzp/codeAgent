from __future__ import annotations

import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


EXECUTION_EVENT_KINDS = {
    "model_request",
    "model_response",
    "action",
    "tool_call",
    "tool_result",
}


class ChatPanel(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("ChatPanel")

        self.messages = QWidget()
        self.messages.setObjectName("MessageList")
        self.messages_layout = QVBoxLayout(self.messages)
        self.messages_layout.setContentsMargins(72, 26, 72, 26)
        self.messages_layout.setSpacing(14)
        self.messages_layout.addStretch(1)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setWidget(self.messages)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.scroll, 1)

    def clear(self) -> None:
        while self.messages_layout.count() > 1:
            item = self.messages_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def show_events(self, events: list[dict]) -> None:
        self.clear()
        for event in events:
            self.append_event(event)

    def append_event(self, event: dict) -> None:
        kind = str(event.get("kind", "event"))
        if kind == "step":
            return
        if kind == "finish":
            self._hide_execution_events()

        card = MessageCard(event)
        row = QFrame()
        row.setObjectName("MessageRow")
        row.setProperty("event_kind", kind)
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(0)
        if _role_for_kind(kind) == "user":
            row_layout.addStretch(1)
            row_layout.addWidget(card)
        else:
            row_layout.addWidget(card)
            row_layout.addStretch(1)
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, row)
        self._scroll_to_bottom()

    def show_final_message(self, message: str) -> None:
        if message:
            self.append_event({"kind": "finish", "message": message, "data": {}, "timestamp": 0})

    def show_error(self, message: str) -> None:
        self.append_event({"kind": "error", "message": message, "data": {}, "timestamp": 0})

    def _scroll_to_bottom(self) -> None:
        bar = self.scroll.verticalScrollBar()
        bar.setValue(bar.maximum())

    def _hide_execution_events(self) -> None:
        for index in range(self.messages_layout.count()):
            item = self.messages_layout.itemAt(index)
            widget = item.widget() if item is not None else None
            if widget is None:
                continue
            if widget.property("event_kind") in EXECUTION_EVENT_KINDS:
                widget.setVisible(False)


class MessageCard(QFrame):
    def __init__(self, event: dict) -> None:
        super().__init__()
        kind = str(event.get("kind", "event"))
        role = _role_for_kind(kind)
        self.setObjectName(f"MessageCard-{role}")
        self.setMaximumWidth(900 if role != "user" else 720)

        label = QLabel(_label_for_kind(kind))
        label.setObjectName("MessageRole")
        summary = QLabel(_summary_for_event(event))
        summary.setWordWrap(True)
        summary.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self.details = QPlainTextEdit()
        self.details.setReadOnly(True)
        self.details.setPlainText(_detail_for_event(event))
        self.details.setVisible(False)
        self.details.setMinimumHeight(140)
        self.details.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.toggle = QPushButton("Details")
        self.toggle.setObjectName("GhostButton")
        self.toggle.setVisible(_has_details(event))
        self.toggle.clicked.connect(self._toggle_details)

        top = QHBoxLayout()
        top.addWidget(label)
        top.addStretch(1)
        top.addWidget(self.toggle)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)
        layout.addLayout(top)
        layout.addWidget(summary)
        layout.addWidget(self.details)

    def _toggle_details(self) -> None:
        next_visible = not self.details.isVisible()
        self.details.setVisible(next_visible)
        self.toggle.setText("Hide" if next_visible else "Details")


def _role_for_kind(kind: str) -> str:
    if kind == "user_message":
        return "user"
    if kind in {"finish", "error"}:
        return kind
    return "agent"


def _label_for_kind(kind: str) -> str:
    labels = {
        "user_message": "You",
        "model_request": "Agent",
        "model_response": "Model",
        "action": "Action",
        "tool_call": "Tool",
        "tool_result": "Result",
        "finish": "输出",
        "error": "Error",
    }
    return labels.get(kind, kind)


def _summary_for_event(event: dict) -> str:
    kind = str(event.get("kind", "event"))
    message = str(event.get("message", ""))
    data = event.get("data") if isinstance(event.get("data"), dict) else {}

    if kind == "model_request":
        step = data.get("step")
        return f"Thinking and calling the model{f' (step {step})' if step else ''}..."
    if kind == "model_response":
        return "Received a model response."
    if kind == "action":
        return f"Next action: {message}"
    if kind == "tool_call":
        args = data.get("args") if isinstance(data.get("args"), dict) else {}
        return f"Calling {message}: {_summarize_args(message, args)}"
    if kind == "tool_result":
        nested = data.get("data") if isinstance(data.get("data"), dict) else {}
        tool = str(data.get("tool", "tool"))
        ok = bool(data.get("ok"))
        if tool == "list_files" and isinstance(nested.get("count"), int):
            return f"{tool} {'succeeded' if ok else 'failed'}: listed {nested['count']} entries."
        if tool == "write_file" and nested.get("path"):
            changed = "changed" if nested.get("changed") else "unchanged"
            return f"{tool} {'succeeded' if ok else 'failed'}: {nested['path']} {changed}."
        if tool == "run_command" and "exit_code" in nested:
            return f"{tool} {'succeeded' if ok else 'failed'}: exit_code={nested['exit_code']}."
        if tool == "read_file":
            return f"{tool} {'succeeded' if ok else 'failed'}: {_summarize_text(message)}"
        return f"{tool} {'succeeded' if ok else 'failed'}."
    if kind == "finish":
        return message
    if kind == "error":
        return message
    return message


def _summarize_args(tool_name: str, args: dict) -> str:
    if tool_name == "write_file":
        content = str(args.get("content", ""))
        return f"{args.get('path', '')} ({len(content.splitlines())} lines, {len(content)} chars)"
    if tool_name == "run_command":
        command = str(args.get("command", ""))
        return command if len(command) <= 120 else command[:117] + "..."
    if "path" in args:
        return str(args.get("path"))
    return "parameters hidden"


def _summarize_text(text: str) -> str:
    payload = text[4:] if text.startswith("ok: ") else text
    lines = payload.splitlines()
    if not lines:
        return "empty output."
    return f"{len(lines)} lines, {len(payload)} chars."


def _detail_for_event(event: dict) -> str:
    data = event.get("data") if isinstance(event.get("data"), dict) else {}
    nested = data.get("data") if isinstance(data.get("data"), dict) else {}

    if event.get("kind") == "tool_result":
        if nested.get("diff"):
            return str(nested["diff"])
        if "stdout" in nested or "stderr" in nested:
            return (
                f"exit_code: {nested.get('exit_code')}\n\n"
                f"stdout:\n{nested.get('stdout') or ''}\n\n"
                f"stderr:\n{nested.get('stderr') or ''}"
            )

    if event.get("kind") == "tool_call":
        return json.dumps(data.get("args", {}), ensure_ascii=False, indent=2)

    return json.dumps(event, ensure_ascii=False, indent=2)


def _has_details(event: dict) -> bool:
    return event.get("kind") in {"tool_call", "tool_result", "model_response", "error"}
