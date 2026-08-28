APP_STYLE = """
QMainWindow {
    background: #ffffff;
}

QWidget {
    color: #202124;
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
    font-size: 14px;
}

QFrame#Sidebar {
    background: #f7f7f7;
    border-right: 1px solid #e5e7eb;
    min-width: 280px;
    max-width: 320px;
}

QFrame#MainArea,
QFrame#ChatPanel,
QWidget#MessageList {
    background: #ffffff;
}

QFrame#TopBar {
    background: #ffffff;
    border-bottom: 1px solid #e5e7eb;
}

QFrame#ChatPanel,
QFrame#MessageRow {
    border: none;
}

QFrame#Composer {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 24px;
    margin: 0 72px 24px 72px;
}

QLabel#BrandTitle {
    color: #202124;
    font-size: 22px;
    font-weight: 700;
}

QLabel#HeaderTitle {
    color: #202124;
    font-size: 16px;
    font-weight: 600;
}

QLabel#PanelTitle {
    color: #111827;
    font-size: 15px;
    font-weight: 600;
}

QLabel#SectionLabel {
    color: #a3a3a3;
    font-size: 13px;
    font-weight: 600;
}

QLabel#ProjectName {
    color: #4b5563;
    font-size: 15px;
    padding: 4px 2px;
}

QLabel#Muted,
QLabel#StatusLabel {
    color: #6b7280;
}

QLabel#MessageRole {
    color: #6b7280;
    font-size: 12px;
    font-weight: 600;
}

QLineEdit,
QSpinBox {
    background: #ffffff;
    color: #111827;
    border: 1px solid #dedede;
    border-radius: 8px;
    padding: 7px 9px;
    selection-background-color: #dbeafe;
}

QTextEdit#ComposerInput {
    background: transparent;
    color: #202124;
    border: none;
    padding: 10px;
    selection-background-color: #dbeafe;
}

QPlainTextEdit {
    background: #f4f4f5;
    color: #111827;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 10px;
    font-family: "Cascadia Code", Consolas, monospace;
    font-size: 12px;
    selection-background-color: #dbeafe;
}

QListWidget#SidebarList {
    background: transparent;
    color: #3f3f46;
    border: none;
    outline: none;
}

QListWidget#SidebarList::item {
    padding: 10px 12px;
    border-radius: 12px;
}

QListWidget#SidebarList::item:selected {
    background: #e9e9e9;
    color: #202124;
}

QPushButton {
    background: #ffffff;
    color: #202124;
    border: 1px solid #dcdcdc;
    border-radius: 10px;
    padding: 8px 12px;
}

QPushButton:hover {
    background: #f3f4f6;
}

QPushButton#SidebarButton {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    text-align: left;
    padding: 10px 12px;
}

QPushButton#IconButton {
    min-width: 36px;
    max-width: 42px;
    padding: 7px;
}

QPushButton#PathButton {
    min-width: 72px;
    max-width: 86px;
    padding: 7px 10px;
}

QPushButton#GhostButton {
    background: transparent;
    color: #6b7280;
    border: 1px solid transparent;
    padding: 4px 8px;
}

QPushButton#GhostButton:hover {
    background: #f4f4f5;
}

QPushButton#SendButton {
    background: #202124;
    color: #ffffff;
    border: none;
    border-radius: 22px;
    min-width: 44px;
    max-width: 44px;
    min-height: 44px;
    max-height: 44px;
    font-size: 20px;
    font-weight: 700;
}

QPushButton#SendButton:disabled,
QPushButton:disabled {
    background: #f3f4f6;
    color: #a3a3a3;
}

QFrame#MessageCard-user,
QFrame#MessageCard-agent,
QFrame#MessageCard-finish,
QFrame#MessageCard-error {
    border-radius: 14px;
    border: 1px solid transparent;
}

QFrame#MessageCard-user {
    background: #f4f4f5;
    border-color: #eeeeee;
}

QFrame#MessageCard-agent {
    background: #ffffff;
    border-color: #ffffff;
}

QFrame#MessageCard-finish {
    background: #ffffff;
    border-radius: 0;
    border-left: none;
    border-right: none;
    border-top: 1px solid #d1d5db;
    border-bottom: 1px solid #d1d5db;
}

QFrame#MessageCard-error {
    background: #fef2f2;
    border-color: #fecaca;
}

QScrollArea {
    border: none;
    background: transparent;
}

QScrollBar:vertical {
    background: transparent;
    width: 10px;
}

QScrollBar::handle:vertical {
    background: #d1d5db;
    border-radius: 5px;
}

QStatusBar {
    background: #ffffff;
    color: #6b7280;
    border-top: 1px solid #f1f3f4;
}
"""
