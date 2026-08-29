from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QTextEdit, QVBoxLayout


class Composer(QFrame):
    run_requested = Signal(str, list)
    skill_picker_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("Composer")
        self._selected_skills: list[str] = []

        self.input = QTextEdit()
        self.input.setObjectName("ComposerInput")
        self.input.setPlaceholderText("给 Code Agent 一个编程任务...")
        self.input.setMinimumHeight(48)
        self.input.setMaximumHeight(84)

        self.send_button = QPushButton("↑")
        self.send_button.setObjectName("SendButton")
        self.send_button.clicked.connect(self._emit_run)

        self.skill_button = QPushButton("+")
        self.skill_button.setObjectName("SkillButton")
        self.skill_button.setToolTip("选择 Skill")
        self.skill_button.clicked.connect(self.skill_picker_requested.emit)

        self.skill_label = QLabel("")
        self.skill_label.setObjectName("SkillBadge")
        self.skill_label.hide()

        shortcut = QShortcut(QKeySequence("Ctrl+Return"), self.input)
        shortcut.activated.connect(self._emit_run)

        meta_row = QHBoxLayout()
        meta_row.addWidget(self.skill_button)
        meta_row.addWidget(self.skill_label)
        meta_row.addStretch(1)

        input_row = QHBoxLayout()
        input_row.addWidget(self.input, 1)
        input_row.addWidget(self.send_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(6)
        layout.addLayout(meta_row)
        layout.addLayout(input_row)

    def set_running(self, running: bool) -> None:
        self.input.setEnabled(not running)
        self.send_button.setEnabled(not running)
        self.skill_button.setEnabled(not running)

    def selected_skills(self) -> list[str]:
        return list(self._selected_skills)

    def set_selected_skills(self, names: list[str]) -> None:
        self._selected_skills = list(dict.fromkeys(name for name in names if name))
        if not self._selected_skills:
            self.skill_label.clear()
            self.skill_label.hide()
            self.skill_button.setToolTip("选择 Skill")
            return

        label = ", ".join(self._selected_skills)
        self.skill_label.setText(f"Skills: {label}")
        self.skill_label.setToolTip(label)
        self.skill_label.show()
        self.skill_button.setToolTip(f"已选择: {label}")

    def _emit_run(self) -> None:
        task = self.input.toPlainText().strip()
        if task:
            self.run_requested.emit(task, self.selected_skills())
            self.input.clear()
