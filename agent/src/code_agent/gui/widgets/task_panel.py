from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from uuid import uuid4

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)


@dataclass
class ChatItem:
    id: str
    title: str


@dataclass
class ProjectItem:
    id: str
    name: str
    path: str
    chats: list[ChatItem] = field(default_factory=list)


def _default_workspace() -> str:
    current = Path.cwd().resolve()
    for base in (current, *current.parents):
        candidate = base / "examples" / "demo_workspace"
        if candidate.exists():
            return str(candidate)
    return str((current / "examples" / "demo_workspace").resolve())


class TaskPanel(QFrame):
    chat_changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("Sidebar")
        self._projects: list[ProjectItem] = []
        self._current_project_id = ""
        self._current_chat_id = ""

        self.workspace_edit = QLineEdit()
        self.workspace_edit.setReadOnly(True)

        self.max_steps = QSpinBox()
        self.max_steps.setRange(1, 30)
        self.max_steps.setValue(8)

        self.new_project_button = QPushButton("新建项目")
        self.new_project_button.setObjectName("SidebarButton")
        self.new_project_button.clicked.connect(self._create_project_from_dialog)

        self.new_chat_button = QPushButton("新建对话")
        self.new_chat_button.setObjectName("SidebarButton")
        self.new_chat_button.clicked.connect(self.create_chat)

        self.project_list = QListWidget()
        self.project_list.setObjectName("SidebarList")
        self.project_list.currentRowChanged.connect(self._select_project_row)

        self.chat_list = QListWidget()
        self.chat_list.setObjectName("SidebarList")
        self.chat_list.currentRowChanged.connect(self._select_chat_row)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        brand = QLabel("Code Agent")
        brand.setObjectName("BrandTitle")
        layout.addWidget(brand)
        layout.addWidget(self.new_project_button)
        layout.addSpacing(12)

        project_label = QLabel("项目")
        project_label.setObjectName("SectionLabel")
        layout.addWidget(project_label)
        layout.addWidget(self.project_list, 1)

        chat_label = QLabel("对话")
        chat_label.setObjectName("SectionLabel")
        layout.addWidget(chat_label)
        layout.addWidget(self.new_chat_button)
        layout.addWidget(self.chat_list, 2)

        settings_label = QLabel("运行设置")
        settings_label.setObjectName("SectionLabel")
        layout.addWidget(settings_label)
        layout.addWidget(QLabel("项目文件夹"))
        layout.addWidget(self.workspace_edit)

        layout.addWidget(QLabel("Max steps"))
        layout.addWidget(self.max_steps)
        self._add_initial_project()

    def set_running(self, running: bool) -> None:
        self.new_project_button.setEnabled(not running)
        self.new_chat_button.setEnabled(not running)
        self.max_steps.setEnabled(not running)
        self.project_list.setEnabled(not running)
        self.chat_list.setEnabled(not running)

    def workspace(self) -> str:
        project = self.current_project()
        return project.path if project is not None else ""

    def current_chat_id(self) -> str:
        return self._current_chat_id

    def current_chat_title(self) -> str:
        chat = self.current_chat()
        return chat.title if chat is not None else "新对话"

    def max_step_count(self) -> int:
        return self.max_steps.value()

    def create_chat(self) -> None:
        project = self.current_project()
        if project is None:
            return
        chat = ChatItem(id=uuid4().hex, title=f"新对话 {len(project.chats) + 1}")
        project.chats.append(chat)
        self._current_chat_id = chat.id
        self._refresh_chats()
        self.chat_changed.emit(chat.id)

    def rename_current_chat(self, title: str) -> None:
        chat = self.current_chat()
        if chat is None:
            return
        compact = " ".join(title.split())
        if not compact:
            return
        chat.title = compact[:28]
        self._refresh_chats()

    def current_project(self) -> ProjectItem | None:
        return next((project for project in self._projects if project.id == self._current_project_id), None)

    def current_chat(self) -> ChatItem | None:
        project = self.current_project()
        if project is None:
            return None
        return next((chat for chat in project.chats if chat.id == self._current_chat_id), None)

    def _add_initial_project(self) -> None:
        workspace = _default_workspace()
        name = Path(workspace).name or "codeAgent"
        project = ProjectItem(id=uuid4().hex, name=name, path=workspace)
        project.chats.append(ChatItem(id=uuid4().hex, title="新对话 1"))
        self._projects.append(project)
        self._current_project_id = project.id
        self._current_chat_id = project.chats[0].id
        self._refresh_projects()
        self._refresh_chats()

    def _create_project_from_dialog(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "选择项目文件夹", self.workspace())
        if not directory:
            return
        path = str(Path(directory).resolve())
        existing = next((project for project in self._projects if project.path == path), None)
        if existing is not None:
            self._current_project_id = existing.id
            if existing.chats:
                self._current_chat_id = existing.chats[0].id
            self._refresh_projects()
            self._refresh_chats()
            self.chat_changed.emit(self._current_chat_id)
            return

        project = ProjectItem(id=uuid4().hex, name=Path(path).name or path, path=path)
        project.chats.append(ChatItem(id=uuid4().hex, title="新对话 1"))
        self._projects.append(project)
        self._current_project_id = project.id
        self._current_chat_id = project.chats[0].id
        self._refresh_projects()
        self._refresh_chats()
        self.chat_changed.emit(self._current_chat_id)

    def _select_project_row(self, row: int) -> None:
        if not 0 <= row < len(self._projects):
            return
        project = self._projects[row]
        if project.id == self._current_project_id:
            return
        self._current_project_id = project.id
        if not project.chats:
            project.chats.append(ChatItem(id=uuid4().hex, title="新对话 1"))
        self._current_chat_id = project.chats[0].id
        self._refresh_chats()
        self.chat_changed.emit(self._current_chat_id)

    def _select_chat_row(self, row: int) -> None:
        project = self.current_project()
        if project is None or not 0 <= row < len(project.chats):
            return
        chat = project.chats[row]
        if chat.id == self._current_chat_id:
            return
        self._current_chat_id = chat.id
        self.chat_changed.emit(chat.id)

    def _refresh_projects(self) -> None:
        self.project_list.blockSignals(True)
        self.project_list.clear()
        current_row = 0
        for index, project in enumerate(self._projects):
            item = QListWidgetItem(project.name)
            item.setToolTip(project.path)
            self.project_list.addItem(item)
            if project.id == self._current_project_id:
                current_row = index
        self.project_list.setCurrentRow(current_row)
        self.project_list.blockSignals(False)
        self._sync_workspace_label()

    def _refresh_chats(self) -> None:
        project = self.current_project()
        self.chat_list.blockSignals(True)
        self.chat_list.clear()
        current_row = 0
        if project is not None:
            for index, chat in enumerate(project.chats):
                self.chat_list.addItem(QListWidgetItem(chat.title))
                if chat.id == self._current_chat_id:
                    current_row = index
            self.chat_list.setCurrentRow(current_row)
        self.chat_list.blockSignals(False)
        self._sync_workspace_label()

    def _sync_workspace_label(self) -> None:
        self.workspace_edit.setText(self.workspace())
