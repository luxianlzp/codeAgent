from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


class RunHistoryStore:
    def __init__(self, workspace: str | Path) -> None:
        self.workspace = Path(workspace).resolve()
        self.runs_dir = self.workspace / ".code-agent" / "runs"

    def load(self, limit: int = 30) -> list[dict]:
        if not self.runs_dir.exists():
            return []

        records: list[dict] = []
        for path in sorted(self.runs_dir.glob("*.json"), reverse=True):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            record = self._normalize_record(payload, path)
            if record is not None:
                records.append(record)
            if len(records) >= limit:
                break
        return records

    def save(
        self,
        *,
        title: str,
        task: str,
        model: str,
        max_steps: int,
        status: str,
        final_message: str,
        selected_skills: list[str],
        ui_events: list[dict],
        raw_events: list[dict],
    ) -> dict:
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        now = datetime.now(timezone.utc).replace(microsecond=0)
        run_id = f"{now.strftime('%Y%m%dT%H%M%SZ')}-{uuid4().hex[:8]}"
        path = self.runs_dir / f"{run_id}.json"
        payload = {
            "schema_version": 1,
            "id": run_id,
            "title": title,
            "task": task,
            "workspace": str(self.workspace),
            "model": model,
            "max_steps": max_steps,
            "status": status,
            "final_message": final_message,
            "selected_skills": selected_skills,
            "created_at": now.isoformat(),
            "ui_events": self._json_safe(ui_events),
            "raw_events": self._json_safe(raw_events),
        }
        tmp_path = path.with_suffix(".tmp")
        tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp_path.replace(path)
        return self._normalize_record(payload, path) or payload

    @staticmethod
    def _normalize_record(payload: dict, path: Path) -> dict | None:
        run_id = str(payload.get("id") or path.stem)
        title = str(payload.get("title") or payload.get("task") or "历史任务")
        ui_events = payload.get("ui_events")
        if not isinstance(ui_events, list):
            return None
        return {
            "id": run_id,
            "title": title,
            "task": str(payload.get("task") or title),
            "workspace": str(payload.get("workspace") or ""),
            "model": str(payload.get("model") or ""),
            "max_steps": int(payload.get("max_steps") or 0),
            "status": str(payload.get("status") or ""),
            "final_message": str(payload.get("final_message") or ""),
            "selected_skills": payload.get("selected_skills") if isinstance(payload.get("selected_skills"), list) else [],
            "created_at": str(payload.get("created_at") or ""),
            "ui_events": ui_events,
            "raw_events": payload.get("raw_events") if isinstance(payload.get("raw_events"), list) else [],
            "path": str(path),
        }

    @staticmethod
    def _json_safe(value: object) -> object:
        return json.loads(json.dumps(value, ensure_ascii=False, default=str))
