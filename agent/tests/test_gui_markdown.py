from __future__ import annotations

import pytest

from code_agent.gui.markdown import render_final_markdown_html


def test_render_final_markdown_html_highlights_fenced_python_code() -> None:
    rendered = render_final_markdown_html("Done\n\n```python\ndef add(a, b):\n    return a + b\n```")

    assert "<pre" in rendered
    assert "python" in rendered
    assert '<span style="color:#1d4ed8; font-weight:600;">def</span>' in rendered
    assert '<span style="color:#1d4ed8; font-weight:600;">return</span>' in rendered


def test_qml_controller_adds_summary_html_for_finish_events() -> None:
    pytest.importorskip("PySide6")
    from code_agent.gui.qml_bridge import QmlController

    rendered = QmlController._summary_html_for_event(
        {"kind": "finish", "message": "Done\n\n```js\nfunction run() { return 1 }\n```", "data": {}}
    )

    assert "<pre" in rendered
    assert "function" in rendered


def test_qml_controller_leaves_non_finish_events_without_summary_html() -> None:
    pytest.importorskip("PySide6")
    from code_agent.gui.qml_bridge import QmlController

    assert QmlController._summary_html_for_event({"kind": "tool_result", "message": "`raw`", "data": {}}) == ""
