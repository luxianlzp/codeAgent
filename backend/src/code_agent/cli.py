from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

from code_agent.core import Agent, AgentConfig
from code_agent.core.env import load_dotenv_files
from code_agent.core.events import TraceEvent
from code_agent.core.result import AgentRunResult
from code_agent.tools import build_default_registry
from code_agent.workspace import Workspace


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the coding agent CLI.")
    parser.add_argument("task", nargs="*", help="Programming task for the agent.")
    parser.add_argument("--workspace", default=".", help="Workspace directory the agent can access.")
    parser.add_argument("--max-steps", type=int, default=None, help="Maximum agent loop steps.")
    parser.add_argument("--json-trace", action="store_true", help="Print the complete run trace as JSON.")
    parser.add_argument("--trace-file", help="Write the complete run trace to a JSON file.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print full model responses and tool details.")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI colors in human-readable output.")
    parser.add_argument("--interactive", "-i", action="store_true", help="Keep the CLI open for multiple tasks.")
    return parser


class Theme:
    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled

    def paint(self, text: str, color: str) -> str:
        if not self.enabled:
            return text
        colors = {
            "dim": "\033[2m",
            "cyan": "\033[36m",
            "blue": "\033[34m",
            "green": "\033[32m",
            "yellow": "\033[33m",
            "red": "\033[31m",
            "magenta": "\033[35m",
            "bold": "\033[1m",
        }
        reset = "\033[0m"
        return f"{colors[color]}{text}{reset}"


def colors_enabled(no_color: bool) -> bool:
    if no_color or os.getenv("NO_COLOR"):
        return False
    return sys.stdout.isatty()


def format_event(event: TraceEvent, verbose: bool = False, theme: Theme | None = None) -> str | None:
    theme = theme or Theme(False)
    if event.kind == "step" and not verbose:
        return None
    if event.kind == "model_request":
        step = event.data.get("step")
        suffix = f" step={step}" if step is not None else ""
        return f"{theme.paint('[model]', 'cyan')} calling model...{theme.paint(suffix, 'dim')}"
    if event.kind == "model_response" and not verbose:
        return None
    if event.kind == "model_response":
        return f"{theme.paint('[model_response]', 'dim')} {_indent(event.message)}"
    if event.kind == "action":
        return f"{theme.paint('[action]', 'magenta')} {theme.paint(event.message, 'bold')}"
    if event.kind == "tool_call":
        args_data = event.data.get("args", {})
        args = (
            json.dumps(args_data, ensure_ascii=False)
            if verbose
            else _summarize_tool_args(event.message, args_data)
        )
        return f"{theme.paint('[tool_call]', 'blue')} {event.message} {theme.paint(args, 'dim')}"
    if event.kind == "tool_result":
        ok = event.data.get("ok")
        status = "ok" if ok else "error"
        label_color = "green" if ok else "red"
        if not verbose:
            tool = event.data.get("tool")
            output = event.message
            if tool == "read_file":
                return _result_line(status, _summarize_text("read", output), label_color, theme)
            if tool == "list_files":
                data = event.data.get("data") or {}
                count = data.get("count")
                if count == 0:
                    return _result_line(status, "listed 0 entries", label_color, theme)
                if isinstance(count, int):
                    preview = _first_payload_line(output)
                    suffix = f": {preview}" if preview else ""
                    return _result_line(status, f"listed {count} entries{suffix}", label_color, theme)
                return _result_line(status, _summarize_text("listed", output), label_color, theme)
            if tool == "run_command":
                exit_code = (event.data.get("data") or {}).get("exit_code")
                if exit_code is not None:
                    return _result_line(status, f"exit_code={exit_code}", label_color, theme)
            if tool == "write_file":
                data = event.data.get("data") or {}
                path = data.get("path")
                changed = data.get("changed")
                suffix = "changed" if changed else "unchanged"
                color = "yellow" if changed else "dim"
                return _result_line(status, f"{path} {theme.paint(suffix, color)}", label_color, theme)
        return _result_line(status, _indent(event.message), label_color, theme)
    if event.kind == "finish":
        return f"{theme.paint('[finish]', 'green')} {event.message}"
    if event.kind == "error":
        return f"{theme.paint('[error]', 'red')} {event.message}"
    if event.kind == "user_message":
        return f"{theme.paint('[user]', 'bold')} {event.message}"
    return f"{theme.paint(f'[{event.kind}]', 'dim')} {event.message}"


def _result_line(status: str, message: str, label_color: str, theme: Theme) -> str:
    return f"{theme.paint(f'[tool_result:{status}]', label_color)} {message}"


def _indent(text: str, spaces: int = 2) -> str:
    prefix = " " * spaces
    return text.replace("\n", "\n" + prefix)


def _summarize_text(verb: str, text: str, max_preview_chars: int = 80) -> str:
    payload = _strip_observation_prefix(text)

    lines = payload.splitlines()
    line_count = len(lines)
    char_count = len(payload)
    preview = lines[0] if lines else payload
    if len(preview) > max_preview_chars:
        preview = preview[: max_preview_chars - 3] + "..."
    if line_count <= 1:
        return f"{verb} {char_count} chars: {preview}"
    return f"{verb} {line_count} lines, {char_count} chars: {preview}"


def _first_payload_line(text: str, max_preview_chars: int = 80) -> str:
    payload = _strip_observation_prefix(text)
    if payload == "(empty)":
        return ""
    first = payload.splitlines()[0] if payload.splitlines() else payload
    if len(first) > max_preview_chars:
        first = first[: max_preview_chars - 3] + "..."
    return first


def _strip_observation_prefix(text: str) -> str:
    if text.startswith("ok: "):
        return text[4:]
    if text.startswith("error: "):
        return text[7:]
    return text


def _summarize_tool_args(tool_name: str, args: object) -> str:
    if not isinstance(args, dict):
        return "{}"

    if tool_name == "write_file":
        path = args.get("path", "(missing path)")
        content = str(args.get("content", ""))
        lines = content.splitlines()
        return f"path={path!r}, content={len(lines)} lines/{len(content)} chars"

    if tool_name == "read_file":
        return f"path={args.get('path', '(missing path)')!r}"

    if tool_name == "list_files":
        return f"path={args.get('path', '.')!r}"

    if tool_name == "run_command":
        command = str(args.get("command", ""))
        if len(command) > 120:
            command = command[:117] + "..."
        return f"command={command!r}"

    compact = json.dumps(args, ensure_ascii=False)
    if len(compact) > 120:
        compact = compact[:117] + "..."
    return compact


def print_result(result: AgentRunResult, json_trace: bool, verbose: bool, theme: Theme) -> None:
    if json_trace:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return

    for event in result.events:
        line = format_event(event, verbose=verbose, theme=theme)
        if line is not None:
            print(line)


def print_event(event: TraceEvent, verbose: bool, theme: Theme) -> None:
    line = format_event(event, verbose=verbose, theme=theme)
    if line is not None:
        print(line, flush=True)


def write_trace_file(result: AgentRunResult, trace_file: str) -> None:
    path = Path(trace_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")


def run_task(
    agent: Agent,
    task: str,
    json_trace: bool,
    verbose: bool,
    trace_file: str | None,
    theme: Theme,
) -> bool:
    on_event = None if json_trace else lambda event: print_event(event, verbose, theme)
    try:
        result = agent.run(task, on_event=on_event)
    except RuntimeError as exc:
        print(f"Runtime error: {exc}", file=sys.stderr)
        return False

    if trace_file:
        write_trace_file(result, trace_file)
        if not json_trace:
            print(f"{theme.paint('[trace_file]', 'yellow')} {trace_file}")

    if json_trace:
        print_result(result, json_trace, verbose, theme)
    return result.ok


def main(argv: list[str] | None = None) -> int:
    load_dotenv_files()

    args = build_parser().parse_args(argv)
    theme = Theme(colors_enabled(args.no_color))
    task = " ".join(args.task).strip()
    if not task and not args.interactive:
        task = input("Task: ").strip()
    if not task and not args.interactive:
        print("No task provided.", file=sys.stderr)
        return 2

    config = AgentConfig.from_env(max_steps=args.max_steps)
    workspace = Workspace(Path(args.workspace))
    tools = build_default_registry(workspace, config)

    from code_agent.llm.openai_client import OpenAICompatibleClient

    try:
        llm = OpenAICompatibleClient(model=config.model, base_url=config.base_url)
    except RuntimeError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    agent = Agent(llm=llm, tools=tools, config=config)

    if args.interactive:
        print(f"{theme.paint('Interactive mode.', 'bold')} Type a task, or type :q to quit.")
        ok = True
        if task:
            ok = run_task(agent, task, args.json_trace, args.verbose, args.trace_file, theme)
        while True:
            next_task = input("\nTask> ").strip()
            if next_task in {":q", ":quit", "exit", "quit"}:
                return 0 if ok else 1
            if not next_task:
                continue
            ok = run_task(agent, next_task, args.json_trace, args.verbose, args.trace_file, theme) and ok

    return 0 if run_task(agent, task, args.json_trace, args.verbose, args.trace_file, theme) else 1


if __name__ == "__main__":
    raise SystemExit(main())
