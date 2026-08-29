from __future__ import annotations

from PySide6.QtCore import QThread
from PySide6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QMainWindow, QMessageBox, QStatusBar, QVBoxLayout, QWidget

from code_agent.core import AgentConfig
from code_agent.gui.widgets.chat_panel import ChatPanel
from code_agent.gui.widgets.composer import Composer
from code_agent.gui.widgets.skill_dialog import SkillDialog
from code_agent.gui.widgets.task_panel import TaskPanel
from code_agent.gui.worker import AgentWorker
from code_agent.skills import SkillError, SkillStore


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Code Agent")
        self.resize(1120, 720)
        self.setMinimumSize(900, 600)
        self._thread: QThread | None = None
        self._worker: AgentWorker | None = None
        self._chat_events: dict[str, list[dict]] = {}
        self._active_chat_id = ""

        self.task_panel = TaskPanel()
        self.chat_panel = ChatPanel()
        self.composer = Composer()
        self.status_label = QLabel("Idle")
        self.status_label.setObjectName("StatusLabel")
        self.step_label = QLabel("Step —")
        self.step_label.setObjectName("StatusLabel")
        self.title_label = QLabel(self.task_panel.current_chat_title())
        self.title_label.setObjectName("HeaderTitle")
        self._active_chat_id = self.task_panel.current_chat_id()
        self._chat_events.setdefault(self._active_chat_id, [])

        main_area = QFrame()
        main_area.setObjectName("MainArea")
        main_layout = QVBoxLayout(main_area)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self._build_header())
        main_layout.addWidget(self.chat_panel, 1)
        main_layout.addWidget(self.composer)

        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(self.task_panel)
        root_layout.addWidget(main_area, 1)

        self.setCentralWidget(root)
        self._build_status_bar()

        self.composer.run_requested.connect(self._run_from_composer)
        self.composer.skill_picker_requested.connect(self._open_skill_picker)
        self.task_panel.chat_changed.connect(self._switch_chat)

    def _build_header(self) -> QFrame:
        header = QFrame()
        header.setObjectName("TopBar")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 14, 24, 14)
        layout.addWidget(self.title_label)
        layout.addStretch(1)
        layout.addWidget(self.status_label)
        return header

    def _build_status_bar(self) -> None:
        status_bar = QStatusBar()
        status_bar.setSizeGripEnabled(False)
        connection = QLabel("●  Connected")
        connection.setObjectName("ConnectionStatus")
        model = QLabel(f"Model  {self.task_panel.model_name()}")
        model.setObjectName("StatusChip")
        status_bar.addWidget(connection)
        status_bar.addPermanentWidget(model)
        status_bar.addPermanentWidget(self.step_label)
        self.setStatusBar(status_bar)

    def _run_from_composer(self, task: str, skill_names: list[str]) -> None:
        if self.task_panel.current_chat_title().startswith("新对话"):
            self.task_panel.rename_current_chat(task)
            self._update_header_title()
        self._run_task(task, self.task_panel.workspace(), self.task_panel.max_step_count(), skill_names)

    def _run_task(self, task: str, workspace: str, max_steps: int, skill_names: list[str]) -> None:
        if not task:
            QMessageBox.warning(self, "Missing task", "Please enter a task.")
            return
        if not workspace:
            QMessageBox.warning(self, "Missing workspace", "Please choose a workspace.")
            return
        if self._thread is not None:
            QMessageBox.information(self, "Running", "Please wait for the current task to finish.")
            return

        self.status_label.setText("Running")
        self.step_label.setText("Step 0")
        self.task_panel.set_running(True)
        self.composer.set_running(True)

        config = AgentConfig.from_env(max_steps=max_steps)
        self._thread = QThread(self)
        self._worker = AgentWorker(task=task, workspace=workspace, config=config, skill_names=skill_names)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.event.connect(self._append_event)
        self._worker.finished.connect(self._handle_finished)
        self._worker.failed.connect(self._handle_failed)
        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._thread.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.finished.connect(self._clear_worker_refs)
        self._thread.start()

    def _handle_finished(self, result: dict) -> None:
        status = str(result.get("status", "finished"))
        self.status_label.setText(status)
        self.step_label.setText("Complete")
        self.task_panel.set_running(False)
        self.composer.set_running(False)

    def _handle_failed(self, error: str) -> None:
        self.status_label.setText("Error")
        self.step_label.setText("Failed")
        self._append_event({"kind": "error", "message": error, "data": {}, "timestamp": 0})
        self.task_panel.set_running(False)
        self.composer.set_running(False)

    def _clear_worker_refs(self) -> None:
        self._thread = None
        self._worker = None

    def _append_event(self, event: dict) -> None:
        if event.get("kind") == "step":
            data = event.get("data") if isinstance(event.get("data"), dict) else {}
            self.step_label.setText(f"Step {data.get('step', '—')}")
            return
        chat_id = self._active_chat_id
        if chat_id:
            self._chat_events.setdefault(chat_id, []).append(event)
        self.chat_panel.append_event(event)

    def _switch_chat(self, chat_id: str) -> None:
        if self._thread is not None:
            QMessageBox.information(self, "Running", "Please wait for the current task to finish.")
            return
        self._active_chat_id = chat_id
        self._chat_events.setdefault(chat_id, [])
        self.chat_panel.show_events(self._chat_events[chat_id])
        self._update_header_title()
        self.status_label.setText("Idle")
        self.step_label.setText("Step —")

    def _update_header_title(self) -> None:
        self.title_label.setText(self.task_panel.current_chat_title())

    def _open_skill_picker(self) -> None:
        workspace = self.task_panel.workspace()
        if not workspace:
            QMessageBox.warning(self, "Missing workspace", "Please choose a workspace.")
            return

        try:
            skills = SkillStore.default_for_workspace(workspace).list()
        except SkillError as exc:
            QMessageBox.warning(self, "Skill error", str(exc))
            return

        if not skills:
            QMessageBox.information(self, "No skills", "当前工作目录没有可用 Skill。")
            return

        dialog = SkillDialog(skills, self.composer.selected_skills(), self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.composer.set_selected_skills(dialog.selected_skill_names())
