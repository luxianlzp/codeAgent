from __future__ import annotations

import json

from code_agent.core import Agent, AgentAction, AgentConfig
from code_agent.core.messages import Message
from code_agent.skills import Skill
from code_agent.tools import build_default_registry
from code_agent.workspace import Workspace


class FakeLLM:
    def __init__(self, responses: list[str]) -> None:
        self._responses = responses
        self.messages: list[list[Message]] = []

    def complete(self, messages: list[Message]) -> str:
        self.messages.append(list(messages))
        return self._responses.pop(0)


class FakeStreamingLLM:
    def __init__(self, chunks: list[str]) -> None:
        self._chunks = chunks

    def complete(self, messages: list[Message]) -> str:
        return "".join(self._chunks)

    def stream_complete(self, messages: list[Message]):
        yield from self._chunks


def test_agent_runs_tool_loop_until_finish(tmp_path) -> None:
    llm = FakeLLM(
        [
            '{"action":"write_file","args":{"path":"hello.txt","content":"hello"}}',
            json.dumps(
                {
                    "action": "run_command",
                    "args": {"command": 'python -c "print(open(\'hello.txt\').read())"'},
                }
            ),
            '{"action":"finish","args":{"message":"Created hello.txt and verified it."}}',
        ]
    )
    workspace = Workspace(tmp_path)
    config = AgentConfig(max_steps=5)
    tools = build_default_registry(workspace, config)
    agent = Agent(llm=llm, tools=tools, config=config)

    result = agent.run("Create a hello file.")

    assert (tmp_path / "hello.txt").read_text(encoding="utf-8") == "hello"
    assert result.status == "finished"
    assert "verified" in result.final_message
    assert result.events[-1].kind == "finish"
    assert any(event.kind == "model_request" for event in result.events)
    assert any(event.kind == "tool_call" and event.message == "write_file" for event in result.events)
    assert any(event.kind == "tool_call" and event.message == "run_command" for event in result.events)


def test_agent_stops_on_invalid_json(tmp_path) -> None:
    llm = FakeLLM(["not json"])
    workspace = Workspace(tmp_path)
    config = AgentConfig(max_steps=3)
    agent = Agent(llm=llm, tools=build_default_registry(workspace, config), config=config)

    result = agent.run("Do something.")

    assert result.status == "finished"
    assert result.events[-1].kind == "finish"
    assert "not valid JSON" in result.final_message


def test_agent_emits_events_to_callback(tmp_path) -> None:
    llm = FakeLLM(['{"action":"finish","args":{"message":"done"}}'])
    workspace = Workspace(tmp_path)
    config = AgentConfig(max_steps=3)
    agent = Agent(llm=llm, tools=build_default_registry(workspace, config), config=config)
    streamed = []

    result = agent.run("Stop.", on_event=streamed.append)

    assert result.ok is True
    assert [event.kind for event in streamed] == [event.kind for event in result.events]


def test_agent_streams_model_deltas_before_parsing_action(tmp_path) -> None:
    llm = FakeStreamingLLM(['{"action":"finish","args":', '{"message":"streamed done"}}'])
    workspace = Workspace(tmp_path)
    config = AgentConfig(max_steps=3)
    agent = Agent(llm=llm, tools=build_default_registry(workspace, config), config=config)

    result = agent.run("Stop.")

    deltas = [event for event in result.events if event.kind == "model_delta"]
    assert [event.message for event in deltas] == ['{"action":"finish","args":', '{"message":"streamed done"}}']
    assert result.status == "finished"
    assert result.final_message == "streamed done"


def test_agent_adds_active_skills_to_system_prompt(tmp_path) -> None:
    llm = FakeLLM(['{"action":"finish","args":{"message":"done"}}'])
    workspace = Workspace(tmp_path)
    config = AgentConfig(max_steps=3)
    agent = Agent(llm=llm, tools=build_default_registry(workspace, config), config=config)
    skill = Skill("testing", tmp_path / "testing.md", "Always run the focused tests.")

    result = agent.run("Stop.", skills=[skill])

    assert result.ok is True
    assert "Active skills" in llm.messages[0][0].content
    assert "Always run the focused tests." in llm.messages[0][0].content
    assert any(event.kind == "skill" and event.message == "testing" for event in result.events)


def test_action_parser_normalizes_missing_args() -> None:
    action = AgentAction.parse('{"action":"list_files"}')

    assert action.name == "list_files"
    assert action.args == {}
