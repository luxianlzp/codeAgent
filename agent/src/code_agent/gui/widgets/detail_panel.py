from __future__ import annotations

import json

from PySide6.QtWidgets import QFrame, QLabel, QPlainTextEdit, QVBoxLayout


class DetailPanel(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("Panel")

        self.title = QLabel("Details")
        self.title.setObjectName("PanelTitle")
        self.subtitle = QLabel("Select an event")
        self.subtitle.setObjectName("Muted")
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)
        layout.addSpacing(8)
        layout.addWidget(self.text, 1)

    def show_event(self, event: dict) -> None:
        kind = str(event.get("kind", "event"))
        message = str(event.get("message", ""))
        self.title.setText(kind)
        self.subtitle.setText(message[:120])
        self.text.setPlainText(_event_detail(event))

    def show_message(self, title: str, message: str) -> None:
        self.title.setText(title)
        self.subtitle.setText("")
        self.text.setPlainText(message)


def _event_detail(event: dict) -> str:
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
