from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
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
        self.setMinimumWidth(420)
        self._skills = skills
        selected = {name.lower() for name in selected_names}

        self.list_widget = QListWidget()
        self.list_widget.setObjectName("SkillList")
        for skill in skills:
            item = QListWidgetItem(skill.name)
            item.setToolTip(str(skill.path))
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            state = Qt.CheckState.Checked if skill.name.lower() in selected else Qt.CheckState.Unchecked
            item.setCheckState(state)
            self.list_widget.addItem(item)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        layout.addWidget(QLabel("当前工作目录可用的 Skill"))
        layout.addWidget(self.list_widget)
        layout.addWidget(buttons)

    def selected_skill_names(self) -> list[str]:
        names: list[str] = []
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            if item.checkState() == Qt.CheckState.Checked:
                names.append(item.text())
        return names
