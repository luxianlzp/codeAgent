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
    assert write_result.data is not None
    assert write_result.data["created"] is True
    assert "+hi" in write_result.data["diff"]


def test_write_file_diff_for_existing_file(tmp_path) -> None:
    registry = build_default_registry(Workspace(tmp_path), AgentConfig())

    registry.run("write_file", {"path": "note.txt", "content": "old\n"})
    result = registry.run("write_file", {"path": "note.txt", "content": "new\n"})

    assert result.ok is True
    assert result.data is not None
    assert result.data["created"] is False
    assert "-old" in result.data["diff"]
    assert "+new" in result.data["diff"]


def test_run_command_blocks_dangerous_command(tmp_path) -> None:
    registry = build_default_registry(Workspace(tmp_path), AgentConfig())

    result = registry.run("run_command", {"command": "rm -rf ."})

    assert result.ok is False
    assert "Blocked dangerous command" in result.output
    assert result.data is not None
    assert result.data["blocked"] is True
