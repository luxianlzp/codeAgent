from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QTextEdit, QVBoxLayout


class Composer(QFrame):
    run_requested = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("Composer")

        self.input = QTextEdit()
        self.input.setObjectName("ComposerInput")
        self.input.setPlaceholderText("给 Code Agent 一个编程任务...")
        self.input.setMinimumHeight(48)
        self.input.setMaximumHeight(84)

        self.send_button = QPushButton("↑")
        self.send_button.setObjectName("SendButton")
        self.send_button.clicked.connect(self._emit_run)

        shortcut = QShortcut(QKeySequence("Ctrl+Return"), self.input)
        shortcut.activated.connect(self._emit_run)

        input_row = QHBoxLayout()
        input_row.addWidget(self.input, 1)
        input_row.addWidget(self.send_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(0)
        layout.addLayout(input_row)

    def set_running(self, running: bool) -> None:
        self.input.setEnabled(not running)
        self.send_button.setEnabled(not running)

    def _emit_run(self) -> None:
        task = self.input.toPlainText().strip()
        if task:
            self.run_requested.emit(task)
            self.input.clear()
