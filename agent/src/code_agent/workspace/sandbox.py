from __future__ import annotations

from pathlib import Path


class Workspace:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).expanduser().resolve()
        if not self.root.exists():
            self.root.mkdir(parents=True)
        if not self.root.is_dir():
            raise ValueError(f"Workspace root is not a directory: {self.root}")

    def resolve(self, path: str | Path = ".") -> Path:
        raw_path = Path(path)
        candidate = raw_path if raw_path.is_absolute() else self.root / raw_path
        resolved = candidate.resolve()
        if resolved != self.root and self.root not in resolved.parents:
            raise ValueError(f"Path escapes workspace: {path}")
        return resolved

    def relative(self, path: str | Path) -> str:
        return str(self.resolve(path).relative_to(self.root))
