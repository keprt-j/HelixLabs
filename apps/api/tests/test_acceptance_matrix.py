from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from helixlabs.repos.json_run_repository import JsonRunRepository
from helixlabs.services.orchestrator import RunOrchestrator
from helixlabs.services.stage_service import StageService


class AcceptanceMatrixTests(unittest.TestCase):
    def _orchestrator(self) -> RunOrchestrator:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        repo = JsonRunRepository(runtime_dir=Path(tmp.name))
        return RunOrchestrator(repo=repo, stage_service=StageService())

    def _run(self, goal: str, run_id: str):
        orch = self._orchestrator()
        run = orch.create_run(run_id=run_id, user_goal=goal)
        guard = 0
        while run.state.value != "MEMORY_UPDATED" and guard < 50:
            if run.state.value == "AWAITING_HUMAN_APPROVAL":
                run = orch.approve(run.run_id, approved=True, approved_by="acceptance", notes="")
            else:
                run = orch.advance(run.run_id)
            self.assertIsNotNone(run)
            guard += 1
        self.assertEqual(run.state.value, "MEMORY_UPDATED")
        return run

    def test_matrix(self):
        cases = [
            ("Optimize ionic conductivity for solid electrolytes while preserving phase stability", "chemistry_materials"),
            ("Optimize online ad placement strategy to maximize weekly conversion under budget constraints", "generic_blackbox"),
            ("Tune recommendation ranking to maximize click-through while controlling diversity drift", "generic_blackbox"),
        ]
        for i, (goal, expected_plugin) in enumerate(cases, start=1):
            run = self._run(goal, f"RUN-ACC-{i}")
            plugin = ((run.artifacts.get("experiment_ir") or {}).get("plugin") or {}).get("selected_plugin")
            norm = run.artifacts.get("normalized_results") or {}
            self.assertEqual(plugin, expected_plugin)
            self.assertGreater(len(norm.get("observations") or []), 0)
            self.assertGreater(len(norm.get("series") or []), 0)
            self.assertGreater(len(norm.get("procedure_trace") or []), 0)
            self.assertIn("fidelity", norm)
            self.assertIn("origin", norm)


if __name__ == "__main__":
    unittest.main()
