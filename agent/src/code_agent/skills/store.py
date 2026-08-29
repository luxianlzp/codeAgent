from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable


_SKILL_REF_RE = re.compile(r"(?<!\w)@([A-Za-z0-9](?:[A-Za-z0-9_.-]*[A-Za-z0-9])?)")
_VALID_SKILL_NAME_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9_.-]*[A-Za-z0-9])?$")


class SkillError(ValueError):
    pass


@dataclass(frozen=True)
class Skill:
    name: str
    path: Path
    content: str


class SkillStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).expanduser().resolve()

    @classmethod
    def default_for_workspace(cls, workspace_root: str | Path) -> "SkillStore":
        return cls(Path(workspace_root) / ".code-agent" / "skills")

    def list(self) -> list[Skill]:
        if not self.root.exists():
            return []
        if not self.root.is_dir():
            raise SkillError(f"Skills path is not a directory: {self.root}")

        skills: list[Skill] = []
        seen: set[str] = set()
        candidates = sorted(self.root.iterdir(), key=lambda path: path.name.lower())
        for candidate in candidates:
            skill = self._load_candidate(candidate)
            if skill is None:
                continue
            key = skill.name.lower()
            if key in seen:
                raise SkillError(f"Duplicate skill name: {skill.name}")
            seen.add(key)
            skills.append(skill)
        return skills

    def load(self, names: Iterable[str]) -> list[Skill]:
        requested = _unique_names(names)
        if not requested:
            return []

        available = {skill.name.lower(): skill for skill in self.list()}
        loaded: list[Skill] = []
        missing: list[str] = []
        for name in requested:
            skill = available.get(name.lower())
            if skill is None:
                missing.append(name)
            else:
                loaded.append(skill)
        if missing:
            available_names = ", ".join(skill.name for skill in self.list()) or "(none)"
            raise SkillError(f"Unknown skill(s): {', '.join(missing)}. Available skills: {available_names}")
        return loaded

    def create(self, name: str) -> Path:
        _validate_skill_name(name)
        path = self.root / name / "SKILL.md"
        if path.exists():
            raise SkillError(f"Skill already exists: {name}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_skill_template(name), encoding="utf-8")
        return path

    def _load_candidate(self, path: Path) -> Skill | None:
        if path.is_dir():
            skill_file = path / "SKILL.md"
            if not skill_file.is_file():
                return None
            name = path.name
            source = skill_file
        elif path.is_file() and path.suffix.lower() == ".md":
            name = path.stem
            source = path
        else:
            return None

        _validate_skill_name(name)
        content = source.read_text(encoding="utf-8").strip()
        if not content:
            raise SkillError(f"Skill is empty: {name}")
        return Skill(name=name, path=source, content=content)


def parse_skill_references(task: str) -> list[str]:
    return _unique_names(match.group(1) for match in _SKILL_REF_RE.finditer(task))


def format_skills_for_prompt(skills: Iterable[Skill]) -> str:
    items = list(skills)
    if not items:
        return ""

    blocks = [
        "Active skills:",
        "The following user-selected skills are additional task guidance. Use them when relevant, but still obey the workspace and tool rules above.",
    ]
    for skill in items:
        blocks.append(f"\n## {skill.name}\n{skill.content}")
    return "\n".join(blocks)


def _unique_names(names: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for raw_name in names:
        name = raw_name.strip()
        if not name:
            continue
        _validate_skill_name(name)
        key = name.lower()
        if key not in seen:
            seen.add(key)
            result.append(name)
    return result


def _validate_skill_name(name: str) -> None:
    if not _VALID_SKILL_NAME_RE.match(name):
        raise SkillError(
            "Skill names must start and end with a letter or number and contain only letters, numbers, dots, underscores, or hyphens."
        )


def _skill_template(name: str) -> str:
    return f"""# {name}

Describe when this skill should be used and what guidance the agent should follow.

## Instructions

- Add concise, concrete instructions here.
- Include project conventions, commands, or review criteria that matter for this skill.
"""
