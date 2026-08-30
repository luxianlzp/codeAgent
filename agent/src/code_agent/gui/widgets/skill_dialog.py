from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
)

from code_agent.skills import Skill


class SkillDialog(QDialog):
    def __init__(self, skills: list[Skill], selected_names: list[str], parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("选择 Skill")
        self.setMinimumSize(520, 420)
        self._skills = skills
        selected = {name.lower() for name in selected_names}
        self.setStyleSheet(_DIALOG_STYLE)

        self.list_widget = QListWidget()
        self.list_widget.setObjectName("SkillList")
        for skill in skills:
            item = QListWidgetItem(f"{skill.name}\n{skill.path}")
            item.setToolTip(str(skill.path))
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            state = Qt.CheckState.Checked if skill.name.lower() in selected else Qt.CheckState.Unchecked
            item.setCheckState(state)
            item.setData(Qt.ItemDataRole.UserRole, skill.name)
            item.setSizeHint(QSize(0, 54))
            self.list_widget.addItem(item)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.setObjectName("DialogButtons")
        ok_button = buttons.button(QDialogButtonBox.StandardButton.Ok)
        cancel_button = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        ok_button.setObjectName("PrimaryDialogButton")
        cancel_button.setObjectName("SecondaryDialogButton")
        ok_button.setText("应用")
        cancel_button.setText("取消")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        header = QFrame()
        header.setObjectName("DialogHeader")
        title = QLabel("选择 Skills")
        title.setObjectName("DialogTitle")
        subtitle = QLabel("为本次 Agent 任务注入当前工作区下的可复用指令。")
        subtitle.setObjectName("DialogSubtitle")
        count = QLabel(f"{len(skills)} available")
        count.setObjectName("CountBadge")
        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.addWidget(title)
        title_row.addStretch(1)
        title_row.addWidget(count)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(5)
        header_layout.addLayout(title_row)
        header_layout.addWidget(subtitle)

        hint = QLabel("勾选后点击“应用”，这些 Skills 会随下一次任务发送给 Agent。")
        hint.setObjectName("DialogHint")
        hint.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(14)
        layout.addWidget(header)
        layout.addWidget(self.list_widget)
        layout.addWidget(hint)
        layout.addWidget(buttons)

    def selected_skill_names(self) -> list[str]:
        names: list[str] = []
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            if item.checkState() == Qt.CheckState.Checked:
                names.append(str(item.data(Qt.ItemDataRole.UserRole)))
        return names


_DIALOG_STYLE = """
QDialog {
    background: #fbfbfc;
}

QLabel {
    color: #202124;
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
}

QLabel#DialogTitle {
    color: #111827;
    font-size: 21px;
    font-weight: 700;
}

QLabel#DialogSubtitle,
QLabel#DialogHint {
    color: #6b7280;
    font-size: 12px;
}

QLabel#CountBadge {
    color: #3946a3;
    background: #f0f3ff;
    border: 1px solid #d8defd;
    border-radius: 8px;
    padding: 4px 9px;
    font-size: 12px;
    font-weight: 600;
}

QListWidget#SkillList {
    background: #ffffff;
    border: 1px solid #dfe3ea;
    border-radius: 10px;
    padding: 6px;
    outline: none;
}

QListWidget#SkillList::item {
    color: #111827;
    border-radius: 8px;
    padding: 8px 10px;
    margin: 2px 0;
}

QListWidget#SkillList::item:hover {
    background: #f6f7f9;
}

QListWidget#SkillList::item:selected {
    background: #e9ecf3;
    color: #111827;
}

QListWidget#SkillList::indicator {
    width: 16px;
    height: 16px;
}

QListWidget#SkillList::indicator:unchecked {
    border: 1px solid #cfd5df;
    border-radius: 4px;
    background: #ffffff;
}

QListWidget#SkillList::indicator:checked {
    border: 1px solid #1f2329;
    border-radius: 4px;
    background: #1f2329;
}

QPushButton {
    min-width: 76px;
    min-height: 34px;
    border-radius: 8px;
    padding: 6px 14px;
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
    font-size: 13px;
}

QPushButton:hover {
    background: #f6f7f9;
}

QDialogButtonBox QPushButton {
    background: #ffffff;
    color: #202124;
    border: 1px solid #dfe3ea;
}

QPushButton#PrimaryDialogButton {
    background: #1f2329;
    color: #ffffff;
    border: 1px solid #1f2329;
    font-weight: 600;
}

QPushButton#PrimaryDialogButton:hover {
    background: #111827;
}

QPushButton#SecondaryDialogButton:hover {
    background: #f6f7f9;
}
"""
