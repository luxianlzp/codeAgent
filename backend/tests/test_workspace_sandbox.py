from __future__ import annotations

import pytest

from code_agent.workspace import Workspace


def test_workspace_allows_relative_paths_inside_root(tmp_path) -> None:
    workspace = Workspace(tmp_path)

    resolved = workspace.resolve("src/main.py")

    assert resolved == tmp_path / "src" / "main.py"


def test_workspace_rejects_parent_escape(tmp_path) -> None:
    workspace = Workspace(tmp_path)

    with pytest.raises(ValueError, match="escapes workspace"):
        workspace.resolve("../outside.txt")
