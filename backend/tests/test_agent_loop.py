from __future__ import annotations

from code_agent.core import Agent, AgentConfig
from code_agent.core.messages import Message
from code_agent.tools import build_default_registry
from code_agent.workspace import Workspace


class FakeLLM:
    def __init__(self, responses: list[str]) -> None:
        self._responses = responses
        self.messages: list[list[Message]] = []

    def complete(self, messages: list[Message]) -> str:
        self.messages.append(list(messages))
        return self._responses.pop(0)


def test_agent_runs_tool_loop_until_finish(tmp_path) -> None:
    llm = FakeLLM(
        [
            '{"action":"write_file","args":{"path":"hello.txt","content":"hello"}}',
            '{"action":"run_command","args":{"command":"python -c \\"print(open(\\\'hello.txt\\\').read())\\""}}',
            '{"action":"finish","args":{"message":"Created hello.txt and verified it."}}',
        ]
    )
    workspace = Workspace(tmp_path)
    config = AgentConfig(max_steps=5)
    tools = build_default_registry(workspace, config)
    agent = Agent(llm=llm, tools=tools, config=config)

    events = agent.run("Create a hello file.")

    assert (tmp_path / "hello.txt").read_text(encoding="utf-8") == "hello"
    assert events[-1].kind == "finish"
    assert "verified" in events[-1].message
    assert any(event.kind == "tool_call" and event.message == "write_file" for event in events)
    assert any(event.kind == "tool_call" and event.message == "run_command" for event in events)


def test_agent_stops_on_invalid_json(tmp_path) -> None:
    llm = FakeLLM(["not json"])
    workspace = Workspace(tmp_path)
    config = AgentConfig(max_steps=3)
    agent = Agent(llm=llm, tools=build_default_registry(workspace, config), config=config)

    events = agent.run("Do something.")

    assert events[-1].kind == "finish"
    assert "not valid JSON" in events[-1].message
