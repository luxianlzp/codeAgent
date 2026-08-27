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
    parser.add_argument("--interactive", "-i", action="store_true", help="Keep the CLI open for multiple tasks.")
    return parser


def format_event(event: TraceEvent) -> str:
    if event.kind == "tool_call":
        return f"[tool_call] {event.message} {json.dumps(event.data.get('args', {}), ensure_ascii=False)}"
    if event.kind == "tool_result":
        ok = event.data.get("ok")
        status = "ok" if ok else "error"
        return f"[tool_result:{status}] {event.message}"
    return f"[{event.kind}] {event.message}"


def print_result(result: AgentRunResult, json_trace: bool) -> None:
    if json_trace:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return

    for event in result.events:
        print(format_event(event))


def run_task(agent: Agent, task: str, json_trace: bool) -> bool:
    try:
        result = agent.run(task)
    except RuntimeError as exc:
        print(f"Runtime error: {exc}", file=sys.stderr)
        return False

    print_result(result, json_trace)
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
            ok = run_task(agent, task, args.json_trace)
        while True:
            next_task = input("\nTask> ").strip()
            if next_task in {":q", ":quit", "exit", "quit"}:
                return 0 if ok else 1
            if not next_task:
                continue
            ok = run_task(agent, next_task, args.json_trace) and ok

    return 0 if run_task(agent, task, args.json_trace) else 1


if __name__ == "__main__":
    raise SystemExit(main())
