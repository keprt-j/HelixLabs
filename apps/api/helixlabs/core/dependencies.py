from __future__ import annotations

from pathlib import Path

from helixlabs.repos.json_run_repository import JsonRunRepository
from helixlabs.services.orchestrator import RunOrchestrator
from helixlabs.services.stage_service import StageService


def _runtime_dir() -> Path:
    # apps/api/helixlabs/core/dependencies.py -> repo root at parents[4]
    repo_root = Path(__file__).resolve().parents[4]
    return repo_root / "data" / "runtime"


repo = JsonRunRepository(runtime_dir=_runtime_dir())
stage_service = StageService()
orchestrator = RunOrchestrator(repo=repo, stage_service=stage_service)
