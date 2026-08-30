from __future__ import annotations

import os
import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QFont
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterSingletonInstance
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtWidgets import QApplication

from code_agent.core.env import load_dotenv_files
from code_agent.gui.qml_bridge import QmlController


def main() -> int:
    load_dotenv_files()
    os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Basic")
    QQuickStyle.setStyle("Basic")

    app = QApplication(sys.argv)
    app.setApplicationName("Code Agent")
    app.setFont(QFont("Microsoft YaHei"))

    controller = QmlController()
    app.aboutToQuit.connect(controller.shutdown)
    qmlRegisterSingletonInstance(QmlController, "CodeAgent", 1, 0, "Backend", controller)

    engine = QQmlApplicationEngine()

    qml_file = Path(__file__).resolve().parent / "qml" / "Main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    if not engine.rootObjects():
        return 1

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
