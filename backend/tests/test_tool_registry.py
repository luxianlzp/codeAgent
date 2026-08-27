from __future__ import annotations

from code_agent.core import AgentConfig
from code_agent.tools import build_default_registry
from code_agent.workspace import Workspace


def test_unknown_tool_returns_error(tmp_path) -> None:
    registry = build_default_registry(Workspace(tmp_path), AgentConfig())

    result = registry.run("missing_tool", {})

    assert result.ok is False
    assert "Unknown tool" in result.output


def test_filesystem_tools_read_and_write(tmp_path) -> None:
    registry = build_default_registry(Workspace(tmp_path), AgentConfig())

    write_result = registry.run("write_file", {"path": "note.txt", "content": "hi"})
    read_result = registry.run("read_file", {"path": "note.txt"})

    assert write_result.ok is True
    assert read_result.ok is True
    assert read_result.output == "hi"
