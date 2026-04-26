from __future__ import annotations

import json
from pathlib import Path

from helixlabs.domain.models import RunRecord


class JsonRunRepository:
    def __init__(self, runtime_dir: Path) -> None:
        self._runtime_dir = runtime_dir
        self._runtime_dir.mkdir(parents=True, exist_ok=True)

    def _run_path(self, run_id: str) -> Path:
        return self._runtime_dir / f"{run_id}.json"

    def save(self, run: RunRecord) -> None:
        path = self._run_path(run.run_id)
        path.write_text(run.model_dump_json(indent=2), encoding="utf-8")

    def get(self, run_id: str) -> RunRecord | None:
        path = self._run_path(run_id)
        if not path.exists():
            return None
        return RunRecord.model_validate(json.loads(path.read_text(encoding="utf-8")))
