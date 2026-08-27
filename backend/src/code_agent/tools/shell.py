from __future__ import annotations

import subprocess
from typing import Any

from code_agent.tools.base import ToolResult
from code_agent.workspace import Workspace


class RunCommandTool:
    name = "run_command"
    description = "Run a shell command in the workspace with a timeout."

    def __init__(self, workspace: Workspace, timeout_seconds: int = 30) -> None:
        self._workspace = workspace
        self._timeout_seconds = timeout_seconds

    def run(self, args: dict[str, Any]) -> ToolResult:
        command = args.get("command")
        if not command:
            return ToolResult(False, "Missing required argument: command")
        try:
            completed = subprocess.run(
                str(command),
                cwd=self._workspace.root,
                shell=True,
                text=True,
                capture_output=True,
                timeout=self._timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            output = (exc.stdout or "") + (exc.stderr or "")
            return ToolResult(False, f"Command timed out after {self._timeout_seconds}s\n{output}")

        output_parts = []
        if completed.stdout:
            output_parts.append(f"stdout:\n{completed.stdout.rstrip()}")
        if completed.stderr:
            output_parts.append(f"stderr:\n{completed.stderr.rstrip()}")
        output = "\n\n".join(output_parts) or "(no output)"
        ok = completed.returncode == 0
        return ToolResult(ok, f"exit_code={completed.returncode}\n{output}")
