from __future__ import annotations

import argparse
import json
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
    parser.add_argument("--interactive", "-i", action="store_true", help="Keep the CLI open for multiple tasks.")
    return parser


def format_event(event: TraceEvent, verbose: bool = False) -> str | None:
    if event.kind == "model_response" and not verbose:
        return None
    if event.kind == "action":
        return f"[action] {event.message}"
    if event.kind == "tool_call":
        return f"[tool_call] {event.message} {json.dumps(event.data.get('args', {}), ensure_ascii=False)}"
    if event.kind == "tool_result":
        ok = event.data.get("ok")
        status = "ok" if ok else "error"
        if not verbose:
            tool = event.data.get("tool")
            output = event.message
            if tool == "read_file":
                return f"[tool_result:{status}] {_summarize_text('read', output)}"
            if tool == "list_files":
                return f"[tool_result:{status}] {_summarize_text('listed', output)}"
            if tool == "run_command":
                exit_code = (event.data.get("data") or {}).get("exit_code")
                if exit_code is not None:
                    return f"[tool_result:{status}] exit_code={exit_code}"
            if tool == "write_file":
                data = event.data.get("data") or {}
                path = data.get("path")
                changed = data.get("changed")
                suffix = "changed" if changed else "unchanged"
                return f"[tool_result:{status}] {path} {suffix}"
        return f"[tool_result:{status}] {event.message}"
    return f"[{event.kind}] {event.message}"


def _summarize_text(verb: str, text: str, max_preview_chars: int = 80) -> str:
    payload = text
    if payload.startswith("ok: "):
        payload = payload[4:]
    elif payload.startswith("error: "):
        payload = payload[7:]

    lines = payload.splitlines()
    line_count = len(lines)
    char_count = len(payload)
    preview = lines[0] if lines else payload
    if len(preview) > max_preview_chars:
        preview = preview[: max_preview_chars - 3] + "..."
    if line_count <= 1:
        return f"{verb} {char_count} chars: {preview}"
    return f"{verb} {line_count} lines, {char_count} chars: {preview}"


def print_result(result: AgentRunResult, json_trace: bool, verbose: bool) -> None:
    if json_trace:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return

    for event in result.events:
        line = format_event(event, verbose=verbose)
        if line is not None:
            print(line)


def write_trace_file(result: AgentRunResult, trace_file: str) -> None:
    path = Path(trace_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")


def run_task(agent: Agent, task: str, json_trace: bool, verbose: bool, trace_file: str | None) -> bool:
    try:
        result = agent.run(task)
    except RuntimeError as exc:
        print(f"Runtime error: {exc}", file=sys.stderr)
        return False

    if trace_file:
        write_trace_file(result, trace_file)
        if not json_trace:
            print(f"[trace_file] {trace_file}")

    print_result(result, json_trace, verbose)
    return result.ok


def main(argv: list[str] | None = None) -> int:
    load_dotenv_files()

    args = build_parser().parse_args(argv)
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
        print("Interactive mode. Type a task, or type :q to quit.")
        ok = True
        if task:
            ok = run_task(agent, task, args.json_trace, args.verbose, args.trace_file)
        while True:
            next_task = input("\nTask> ").strip()
            if next_task in {":q", ":quit", "exit", "quit"}:
                return 0 if ok else 1
            if not next_task:
                continue
            ok = run_task(agent, next_task, args.json_trace, args.verbose, args.trace_file) and ok

    return 0 if run_task(agent, task, args.json_trace, args.verbose, args.trace_file) else 1


if __name__ == "__main__":
    raise SystemExit(main())
