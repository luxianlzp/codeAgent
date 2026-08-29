from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from code_agent.core.env import load_dotenv_files
from code_agent.gui.main_window import MainWindow
from code_agent.gui.styles import APP_STYLE


def main() -> int:
    load_dotenv_files()
    app = QApplication(sys.argv)
    app.setApplicationName("Code Agent")
    app.setStyleSheet(APP_STYLE)

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
