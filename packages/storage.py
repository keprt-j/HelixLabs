from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from packages.models import ExperimentRun, ProvenanceEvent, utc_now


class JsonStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.runtime_dir = root / "data" / "runtime"
        self.runtime_dir.mkdir(parents=True, exist_ok=True)
        self.runs_path = self.runtime_dir / "runs.json"
        self.events_path = self.runtime_dir / "provenance_events.json"
        self._ensure_file(self.runs_path, {})
        self._ensure_file(self.events_path, {})

    def _ensure_file(self, path: Path, default: Any) -> None:
        if not path.exists():
            path.write_text(json.dumps(default, indent=2), encoding="utf-8")

    def _read(self, path: Path) -> Any:
        return json.loads(path.read_text(encoding="utf-8"))

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")

    def create_run(self, user_goal: str) -> ExperimentRun:
        runs = self._read(self.runs_path)
        run_id = f"RUN-{len(runs) + 1:03d}"
        run = ExperimentRun(
            id=run_id,
            title="HelixLabs research run",
            user_goal=user_goal,
        )
        runs[run_id] = run.model_dump(mode="json")
        self._write(self.runs_path, runs)
        return run

    def get_run(self, run_id: str) -> ExperimentRun:
        runs = self._read(self.runs_path)
        if run_id not in runs:
            raise KeyError(run_id)
        return ExperimentRun.model_validate(runs[run_id])

    def save_run(self, run: ExperimentRun) -> ExperimentRun:
        runs = self._read(self.runs_path)
        run.updated_at = utc_now()
        runs[run.id] = run.model_dump(mode="json")
        self._write(self.runs_path, runs)
        return run

    def add_event(self, event: ProvenanceEvent) -> ProvenanceEvent:
        events = self._read(self.events_path)
        events.setdefault(event.run_id, []).append(event.model_dump(mode="json"))
        self._write(self.events_path, events)
        return event

    def get_events(self, run_id: str) -> list[ProvenanceEvent]:
        events = self._read(self.events_path)
        return [ProvenanceEvent.model_validate(item) for item in events.get(run_id, [])]


def load_json(root: Path, relative_path: str) -> Any:
    return json.loads((root / relative_path).read_text(encoding="utf-8"))
