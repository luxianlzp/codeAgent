from __future__ import annotations

import argparse
from pathlib import Path
import sys

from code_agent.core import Agent, AgentConfig
from code_agent.tools import build_default_registry
from code_agent.workspace import Workspace


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the coding agent CLI.")
    parser.add_argument("task", nargs="*", help="Programming task for the agent.")
    parser.add_argument("--workspace", default=".", help="Workspace directory the agent can access.")
    parser.add_argument("--max-steps", type=int, default=None, help="Maximum agent loop steps.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    task = " ".join(args.task).strip()
    if not task:
        task = input("Task: ").strip()
    if not task:
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

    events = agent.run(task)
    for event in events:
        print(f"[{event.kind}] {event.message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
