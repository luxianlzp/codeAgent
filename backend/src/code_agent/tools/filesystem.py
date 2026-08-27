from __future__ import annotations

import difflib
from typing import Any

from code_agent.tools.base import ToolResult
from code_agent.workspace import Workspace


class ListFilesTool:
    name = "list_files"
    description = "List files and directories inside the workspace."

    def __init__(self, workspace: Workspace) -> None:
        self._workspace = workspace

    def run(self, args: dict[str, Any]) -> ToolResult:
        path = self._workspace.resolve(args.get("path", "."))
        if not path.is_dir():
            return ToolResult(False, f"Not a directory: {path}")
        entries = []
        for child in sorted(path.iterdir(), key=lambda item: item.name.lower()):
            suffix = "/" if child.is_dir() else ""
            entries.append(f"{child.relative_to(self._workspace.root)}{suffix}")
        return ToolResult(True, "\n".join(entries) or "(empty)")


class ReadFileTool:
    name = "read_file"
    description = "Read a UTF-8 text file inside the workspace."

    def __init__(self, workspace: Workspace) -> None:
        self._workspace = workspace

    def run(self, args: dict[str, Any]) -> ToolResult:
        if "path" not in args:
            return ToolResult(False, "Missing required argument: path")
        path = self._workspace.resolve(args["path"])
        if not path.is_file():
            return ToolResult(False, f"Not a file: {args['path']}")
        try:
            return ToolResult(True, path.read_text(encoding="utf-8"))
        except UnicodeDecodeError as exc:
            return ToolResult(False, f"File is not valid UTF-8 text: {exc}")


class WriteFileTool:
    name = "write_file"
    description = "Write a UTF-8 text file inside the workspace."

    def __init__(self, workspace: Workspace) -> None:
        self._workspace = workspace

    def run(self, args: dict[str, Any]) -> ToolResult:
        if "path" not in args:
            return ToolResult(False, "Missing required argument: path")
        if "content" not in args:
            return ToolResult(False, "Missing required argument: content")
        path = self._workspace.resolve(args["path"])
        relative_path = str(path.relative_to(self._workspace.root))
        new_content = str(args["content"])
        old_content = path.read_text(encoding="utf-8") if path.exists() else None
        diff = _build_diff(relative_path, old_content, new_content)

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(new_content, encoding="utf-8")

        action = "Created" if old_content is None else "Updated"
        changed = old_content != new_content
        return ToolResult(
            True,
            f"{action} {relative_path}",
            {
                "path": relative_path,
                "created": old_content is None,
                "changed": changed,
                "diff": diff,
            },
        )


def _build_diff(path: str, old_content: str | None, new_content: str) -> str:
    old_lines = [] if old_content is None else old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)
    fromfile = "/dev/null" if old_content is None else f"a/{path}"
    tofile = f"b/{path}"
    return "".join(difflib.unified_diff(old_lines, new_lines, fromfile=fromfile, tofile=tofile))
