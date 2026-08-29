APP_STYLE = """
QMainWindow {
    background: #f6f7f9;
}

QWidget {
    color: #202124;
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
    font-size: 14px;
}

QLabel#FieldLabel {
    color: #5f6b7a;
    font-size: 12px;
    font-weight: 600;
    margin-top: 3px;
}

QFrame#Sidebar {
    background: #f7f8fa;
    border-right: 1px solid #e6e8ec;
    min-width: 292px;
    max-width: 312px;
}

QFrame#MainArea,
QFrame#ChatPanel,
QWidget#MessageList {
    background: #fbfbfc;
}

QFrame#TopBar {
    background: #fbfbfc;
    border-bottom: 1px solid #e7e9ee;
}

QFrame#ChatPanel,
QFrame#MessageRow {
    border: none;
}

QFrame#Composer {
    background: #ffffff;
    border: 1px solid #dfe3ea;
    border-radius: 8px;
    margin: 0 36px 18px 36px;
}

QLabel#BrandTitle {
    color: #111827;
    font-size: 24px;
    font-weight: 700;
}

QLabel#HeaderTitle {
    color: #111827;
    font-size: 17px;
    font-weight: 600;
}

QLabel#PanelTitle {
    color: #111827;
    font-size: 15px;
    font-weight: 600;
}

QLabel#SectionLabel {
    color: #8b93a1;
    font-size: 12px;
    font-weight: 600;
}

QLabel#ProjectName {
    color: #4b5563;
    font-size: 15px;
    padding: 4px 2px;
}

QLabel#Muted,
QLabel#StatusLabel {
    color: #7a8494;
}

QLabel#ConnectionStatus {
    color: #16845b;
    font-size: 12px;
    font-weight: 600;
}

QLabel#StatusChip {
    color: #64748b;
    font-size: 12px;
    padding-left: 16px;
}

QFrame#EmptyState {
    background: #ffffff;
    border: 1px solid #e5e9f0;
    border-radius: 12px;
}

QLabel#EmptyTitle {
    color: #172033;
    font-size: 20px;
    font-weight: 700;
}

QLabel#EmptyExamples {
    color: #536174;
    background: #f7f9fc;
    border: 1px solid #edf0f5;
    border-radius: 8px;
    padding: 10px 12px;
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
    border: 1px solid #dfe3ea;
    border-radius: 8px;
    padding: 8px 10px;
    selection-background-color: #dbeafe;
}

QLineEdit:focus,
QSpinBox:focus {
    border: 1px solid #9aa8ff;
}

QTextEdit#ComposerInput {
    background: transparent;
    color: #202124;
    border: none;
    padding: 5px 4px;
    selection-background-color: #dbeafe;
}

QPlainTextEdit {
    background: #f6f7f9;
    color: #111827;
    border: 1px solid #e1e5ec;
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
    border-radius: 8px;
    margin: 2px 0;
}

QListWidget#SidebarList::item:selected {
    background: #e9ecf3;
    color: #111827;
}

QPushButton {
    background: #ffffff;
    color: #202124;
    border: 1px solid #dfe3ea;
    border-radius: 8px;
    padding: 8px 12px;
}

QPushButton:hover {
    background: #f6f7f9;
    border-color: #cfd5df;
}

QPushButton#SidebarButton {
    background: #ffffff;
    border: 1px solid #dfe3ea;
    text-align: left;
    padding: 10px 12px;
}

QPushButton#IconButton {
    min-width: 36px;
    max-width: 42px;
    padding: 7px;
}

QPushButton#GhostButton {
    background: transparent;
    color: #6b7280;
    border: 1px solid transparent;
    padding: 4px 8px;
}

QPushButton#GhostButton:hover {
    background: #f1f3f6;
}

QPushButton#SendButton {
    background: #1f2329;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    min-width: 42px;
    max-width: 42px;
    min-height: 42px;
    max-height: 42px;
    font-size: 17px;
    font-weight: 700;
}

QPushButton#SendButton:hover {
    background: #111827;
}

QPushButton#SkillButton {
    background: #ffffff;
    color: #202124;
    border: 1px solid #dfe3ea;
    border-radius: 8px;
    min-width: 34px;
    max-width: 34px;
    min-height: 34px;
    max-height: 34px;
    padding: 0;
    font-size: 18px;
    font-weight: 600;
}

QLabel#SkillBadge {
    background: #f0f3ff;
    color: #3946a3;
    border: 1px solid #d8defd;
    border-radius: 8px;
    padding: 4px 8px;
    font-size: 12px;
}

QPushButton#SendButton:disabled,
QPushButton:disabled {
    background: #f1f3f6;
    color: #a0a8b5;
}

QFrame#MessageCard-user,
QFrame#MessageCard-agent,
QFrame#MessageCard-finish,
QFrame#MessageCard-error {
    border-radius: 8px;
    border: 1px solid transparent;
}

QFrame#MessageCard-user {
    background: #eef1f6;
    border-color: #e2e6ee;
}

QFrame#MessageCard-agent[event_kind="tool_call"],
QFrame#MessageCard-agent[event_kind="tool_result"] {
    background: #f8fafc;
    border-color: #dfe6ef;
}

QFrame#MessageCard-agent[event_kind="tool_call"] QLabel#MessageRole,
QFrame#MessageCard-agent[event_kind="tool_result"] QLabel#MessageRole {
    color: #4354b8;
}

QFrame#MessageCard-agent {
    background: #ffffff;
    border-color: #ebedf2;
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
    background: #fff1f2;
    border-color: #fecdd3;
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
    background: #cbd2dc;
    border-radius: 5px;
}

QStatusBar {
    background: #fbfbfc;
    color: #7a8494;
    border-top: 1px solid #eceef2;
}
"""
