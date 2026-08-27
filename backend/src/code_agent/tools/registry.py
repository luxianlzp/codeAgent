from __future__ import annotations

from typing import Any

from code_agent.core.config import AgentConfig
from code_agent.tools.base import Tool, ToolResult
from code_agent.tools.filesystem import ListFilesTool, ReadFileTool, WriteFileTool
from code_agent.tools.shell import RunCommandTool
from code_agent.workspace import Workspace


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def run(self, name: str, args: dict[str, Any]) -> ToolResult:
        tool = self._tools.get(name)
        if tool is None:
            return ToolResult(False, f"Unknown tool: {name}")
        try:
            return tool.run(args)
        except Exception as exc:
            return ToolResult(False, f"{type(exc).__name__}: {exc}")

    def descriptions(self) -> str:
        return "\n".join(f"- {tool.name}: {tool.description}" for tool in self._tools.values())


def build_default_registry(workspace: Workspace, config: AgentConfig) -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(ListFilesTool(workspace))
    registry.register(ReadFileTool(workspace))
    registry.register(WriteFileTool(workspace))
    registry.register(RunCommandTool(workspace, timeout_seconds=config.command_timeout_seconds))
    return registry
