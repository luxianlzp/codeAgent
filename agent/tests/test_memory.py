from __future__ import annotations

from code_agent.core.memory import build_memory_context, load_project_memory


def test_load_project_memory_reads_workspace_memory_file(tmp_path) -> None:
    memory_dir = tmp_path / ".code-agent"
    memory_dir.mkdir()
    (memory_dir / "memory.md").write_text("Preferred test command: python -m pytest", encoding="utf-8")

    memory = load_project_memory(tmp_path)

    assert memory == "Preferred test command: python -m pytest"


def test_load_project_memory_is_empty_when_file_is_missing(tmp_path) -> None:
    assert load_project_memory(tmp_path) == ""


def test_build_memory_context_combines_three_layers() -> None:
    context = build_memory_context(
        short_term_memory="Previous task: fixed calculator.py.",
        long_term_memory="Preferred test command: python -m pytest",
    )

    assert "Working memory is maintained inside the current agent loop" in context
    assert "Short-term conversation memory" in context
    assert "Previous task: fixed calculator.py." in context
    assert "Long-term project memory" in context
    assert "Preferred test command: python -m pytest" in context


def test_build_memory_context_empty_without_persisted_memory() -> None:
    assert build_memory_context() == ""
