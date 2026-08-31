from __future__ import annotations

from pathlib import Path
from typing import Any


MAX_CONTEXT_CHARS = 2400
MAX_TURNS = 3
MAX_TOOL_ITEMS_PER_TURN = 8


def build_conversation_context(raw_events: list[dict[str, Any]]) -> str:
    turns = _completed_turns(raw_events)
    if not turns:
        return ""

    selected = turns[-MAX_TURNS:]
    lines = [
        "Previous tasks in this chat, summarized for continuity:",
    ]
    for index, turn in enumerate(selected, start=1):
        lines.append(f"{index}. Task: {_compact_line(turn['task'], 180)}")
        if turn["final"]:
            lines.append(f"   Result: {_compact_line(turn['final'], 220)}")
        tool_lines = turn["tools"][:MAX_TOOL_ITEMS_PER_TURN]
        if tool_lines:
            lines.append(f"   Tool summary: {'; '.join(tool_lines)}")
        files = sorted(turn["files"])
        if files:
            lines.append(f"   Relevant files: {', '.join(files[:8])}")

    context = "\n".join(lines)
    if len(context) <= MAX_CONTEXT_CHARS:
        return context
    return context[: MAX_CONTEXT_CHARS - 3].rstrip() + "..."


def _completed_turns(raw_events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    turns: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    for event in raw_events:
        kind = str(event.get("kind", ""))
        message = str(event.get("message", ""))
        data = _event_data(event)

        if kind == "user_message":
            if current and current["final"]:
                turns.append(current)
            current = {"task": message, "final": "", "tools": [], "files": set()}
            continue

        if current is None:
            continue

        if kind == "tool_call":
            tool = message
            args = data.get("args") if isinstance(data.get("args"), dict) else {}
            summary = _summarize_tool_call(tool, args)
            if summary:
                current["tools"].append(summary)
            _collect_files_from_tool_call(current["files"], tool, args)
            continue

        if kind == "tool_result":
            tool = str(data.get("tool", "tool"))
            ok = bool(data.get("ok"))
            nested = data.get("data") if isinstance(data.get("data"), dict) else {}
            summary = _summarize_tool_result(tool, ok, nested)
            if summary:
                current["tools"].append(summary)
            path = nested.get("path")
            if isinstance(path, str) and path:
                current["files"].add(_display_path(path))
            continue

        if kind in {"finish", "error"}:
            current["final"] = message or kind
            turns.append(current)
            current = None

    return turns


def _summarize_tool_call(tool: str, args: dict[str, Any]) -> str:
    if tool in {"read_file", "write_file"}:
        path = _display_path(str(args.get("path", "")))
        return f"{tool}({path})" if path else tool
    if tool == "list_files":
        path = _display_path(str(args.get("path", ".")))
        return f"list_files({path})"
    if tool == "run_command":
        command = _compact_line(str(args.get("command", "")).strip(), 100)
        return f"run_command({command})" if command else "run_command"
    return tool


def _summarize_tool_result(tool: str, ok: bool, data: dict[str, Any]) -> str:
    status = "ok" if ok else "failed"
    if tool == "run_command" and "exit_code" in data:
        return f"run_command exit_code={data['exit_code']}"
    if tool == "write_file" and data.get("path"):
        changed = "changed" if data.get("changed") else "unchanged"
        return f"write_file {changed}"
    if tool == "list_files" and isinstance(data.get("count"), int):
        return f"list_files count={data['count']}"
    return f"{tool} {status}"


def _collect_files_from_tool_call(files: set[str], tool: str, args: dict[str, Any]) -> None:
    if tool in {"read_file", "write_file"}:
        path = str(args.get("path", "")).strip()
        if path:
            files.add(_display_path(path))


def _display_path(path: str) -> str:
    normalized = path.replace("\\", "/").strip()
    if not normalized:
        return ""
    return Path(normalized).name or normalized


def _compact_line(text: str, limit: int) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def _event_data(event: dict[str, Any]) -> dict[str, Any]:
    data = event.get("data")
    return data if isinstance(data, dict) else {}
