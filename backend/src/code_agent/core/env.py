from __future__ import annotations

from pathlib import Path


def load_dotenv_files() -> None:
    try:
        from dotenv import load_dotenv
    except ModuleNotFoundError:
        return

    backend_dir = Path(__file__).resolve().parents[3]
    project_dir = backend_dir.parent
    candidates = [
        project_dir / ".env",
        backend_dir / ".env",
        Path.cwd() / ".env",
    ]
    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if resolved.is_file():
            load_dotenv(resolved, override=False)
