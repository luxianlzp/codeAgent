from __future__ import annotations

import pytest

from code_agent.skills import SkillError, SkillStore, format_skills_for_prompt, parse_skill_references


def test_skill_store_loads_directory_skills(tmp_path) -> None:
    skill_file = tmp_path / "review" / "SKILL.md"
    skill_file.parent.mkdir()
    skill_file.write_text("# Review\nCheck tests before finishing.", encoding="utf-8")

    store = SkillStore(tmp_path)

    skills = store.list()

    assert [skill.name for skill in skills] == ["review"]
    assert skills[0].content == "# Review\nCheck tests before finishing."


def test_skill_store_loads_markdown_file_skills(tmp_path) -> None:
    (tmp_path / "python.md").write_text("Prefer pathlib.", encoding="utf-8")

    skill = SkillStore(tmp_path).load(["python"])[0]

    assert skill.name == "python"
    assert skill.content == "Prefer pathlib."


def test_skill_store_reports_unknown_skill(tmp_path) -> None:
    store = SkillStore(tmp_path)

    with pytest.raises(SkillError, match="Unknown skill"):
        store.load(["missing"])


def test_skill_store_creates_template(tmp_path) -> None:
    path = SkillStore(tmp_path).create("docs")

    assert path == tmp_path.resolve() / "docs" / "SKILL.md"
    assert "# docs" in path.read_text(encoding="utf-8")


def test_parse_skill_references_deduplicates_case_insensitively() -> None:
    assert parse_skill_references("Use @python and @review.check, then @Python.") == [
        "python",
        "review.check",
    ]


def test_format_skills_for_prompt_includes_selected_skill_content(tmp_path) -> None:
    path = tmp_path / "testing.md"
    path.write_text("Run pytest.", encoding="utf-8")
    skill = SkillStore(tmp_path).load(["testing"])[0]

    prompt = format_skills_for_prompt([skill])

    assert "Active skills" in prompt
    assert "## testing" in prompt
    assert "Run pytest." in prompt
