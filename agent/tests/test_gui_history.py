from __future__ import annotations

import json

from code_agent.gui.history import RunHistoryStore
from code_agent.gui.qml_bridge import QmlController


def test_run_history_store_saves_and_loads_records(tmp_path) -> None:
    store = RunHistoryStore(tmp_path)

    saved = store.save(
        title="Fix calculator",
        task="Fix calculator.py and run tests",
        model="gpt-test",
        max_steps=8,
        status="finished",
        final_message="Task completed",
        selected_skills=["python-review"],
        ui_events=[{"kind": "finish", "summary": "Task completed"}],
        raw_events=[{"kind": "finish", "message": "Task completed"}],
    )

    loaded = store.load()
    payload = json.loads((tmp_path / ".code-agent" / "runs" / f"{saved['id']}.json").read_text(encoding="utf-8"))

    assert loaded[0]["title"] == "Fix calculator"
    assert loaded[0]["status"] == "finished"
    assert loaded[0]["ui_events"][0]["kind"] == "finish"
    assert payload["task"] == "Fix calculator.py and run tests"


def test_qml_controller_appends_multiple_tasks_in_same_chat() -> None:
    controller = QmlController()

    controller._active_task = "first"
    controller._append_event({"kind": "user_message", "message": "first", "data": {}})
    controller._append_event({"kind": "finish", "message": "first done", "data": {}})
    controller._active_task = "second"
    controller._clear_stream_indexes_for_chat(controller.currentChatId)
    controller._append_event({"kind": "user_message", "message": "second", "data": {}})
    controller._append_event({"kind": "finish", "message": "second done", "data": {}})

    summaries = [event["summary"] for event in controller.events]

    assert "first" in summaries
    assert "second" in summaries
    assert "first done" in summaries
    assert "second done" in summaries
