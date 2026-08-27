from __future__ import annotations

import json

from code_agent.cli import format_event, write_trace_file
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

    line = format_event(event, verbose=False)

    assert line is not None
    assert "read 3 lines" in line
    assert "line2" not in line
