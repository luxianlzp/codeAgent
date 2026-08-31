from __future__ import annotations

from pathlib import Path


PROJECT_MEMORY_RELATIVE_PATH = Path(".code-agent") / "memory.md"
MAX_PROJECT_MEMORY_CHARS = 2000


def load_project_memory(workspace: str | Path) -> str:
    path = Path(workspace).resolve() / PROJECT_MEMORY_RELATIVE_PATH
    if not path.exists():
        return ""
    try:
        content = path.read_text(encoding="utf-8").strip()
    except OSError:
        return ""
    return _truncate(content, MAX_PROJECT_MEMORY_CHARS)


def build_memory_context(
    *,
    short_term_memory: str = "",
    long_term_memory: str = "",
) -> str:
    sections = []
    if long_term_memory.strip():
        sections.append("Long-term project memory (.code-agent/memory.md):\n" + long_term_memory.strip())
    if short_term_memory.strip():
        sections.append("Short-term conversation memory:\n" + short_term_memory.strip())
    if not sections:
        return ""
    sections.insert(
        0,
        "Working memory is maintained inside the current agent loop: "
        "the current task, recent actions, and tool observations stay available while this run is active.",
    )
    return "\n\n".join(sections)


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."
