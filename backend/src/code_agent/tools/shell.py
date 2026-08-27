from __future__ import annotations

import shlex
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
        command_text = str(command)
        blocked_reason = _blocked_command_reason(command_text)
        if blocked_reason:
            return ToolResult(
                False,
                f"Blocked dangerous command: {blocked_reason}",
                {"command": command_text, "blocked": True, "reason": blocked_reason},
            )

        try:
            completed = subprocess.run(
                command_text,
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
        return ToolResult(
            ok,
            f"exit_code={completed.returncode}\n{output}",
            {
                "command": command_text,
                "exit_code": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            },
        )


def _blocked_command_reason(command: str) -> str | None:
    lowered = command.lower().strip()
    if not lowered:
        return "empty command"

    try:
        tokens = [token.lower() for token in shlex.split(command, posix=False)]
    except ValueError:
        tokens = lowered.replace(";", " ").replace("&", " ").replace("|", " ").split()

    joined = " ".join(tokens)
    first = tokens[0] if tokens else ""
    destructive_commands = {
        "rm",
        "del",
        "erase",
        "rmdir",
        "rd",
        "format",
        "shutdown",
        "reboot",
        "reg",
        "diskpart",
    }
    if first in destructive_commands:
        return f"`{first}` is blocked"
    if joined.startswith("git reset") or joined.startswith("git clean"):
        return "destructive git command is blocked"
    if " remove-item " in f" {joined} ":
        return "PowerShell Remove-Item is blocked"
    if " set-executionpolicy " in f" {joined} ":
        return "PowerShell execution policy changes are blocked"
    if " -rf " in f" {joined} " or " /s " in f" {joined} ":
        return "recursive destructive flags are blocked"
    return None
