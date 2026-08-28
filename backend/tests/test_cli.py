from __future__ import annotations

import json

from code_agent.cli import Theme, format_event, write_trace_file
from code_agent.core.events import TraceEvent
from code_agent.core.result import AgentRunResult


def test_write_trace_file(tmp_path) -> None:
    result = AgentRunResult("finished", "done", [TraceEvent("finish", "done")])
    trace_file = tmp_path / "traces" / "run.json"

    write_trace_file(result, str(trace_file))

    payload = json.loads(trace_file.read_text(encoding="utf-8"))
    assert payload["status"] == "finished"
    assert payload["final_message"] == "done"


def test_format_event_summarizes_read_file_output() -> None:
    event = TraceEvent(
        "tool_result",
        "ok: line1\nline2\nline3",
        {"tool": "read_file", "ok": True},
    )

    line = format_event(event, verbose=False, theme=Theme(False))

    assert line is not None
    assert "read 3 lines" in line
    assert "line2" not in line


def test_format_event_summarizes_empty_list_files() -> None:
    event = TraceEvent(
        "tool_result",
        "ok: (empty)",
        {"tool": "list_files", "ok": True, "data": {"count": 0, "entries": []}},
    )

    line = format_event(event, verbose=False, theme=Theme(False))

    assert line == "[tool_result:ok] listed 0 entries"


def test_format_event_can_colorize_output() -> None:
    event = TraceEvent("action", "write_file")

    line = format_event(event, verbose=False, theme=Theme(True))

    assert line is not None
    assert "\033[" in line


def test_format_event_summarizes_write_file_tool_call() -> None:
    event = TraceEvent(
        "tool_call",
        "write_file",
        {"args": {"path": "page.html", "content": "<html>\n<body>long content</body>\n</html>"}},
    )

    compact = format_event(event, verbose=False, theme=Theme(False))
    verbose = format_event(event, verbose=True, theme=Theme(False))

    assert compact is not None
    assert "path='page.html'" in compact
    assert "content=3 lines" in compact
    assert "<html>" not in compact
    assert verbose is not None
    assert "<html>" in verbose
