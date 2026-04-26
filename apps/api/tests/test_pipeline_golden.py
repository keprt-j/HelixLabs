from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from helixlabs.repos.json_run_repository import JsonRunRepository
from helixlabs.services.orchestrator import RunOrchestrator
from helixlabs.services.stage_service import StageService


class PipelineGoldenTests(unittest.TestCase):
    def _orchestrator(self) -> RunOrchestrator:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        repo = JsonRunRepository(runtime_dir=Path(tmp.name))
        return RunOrchestrator(repo=repo, stage_service=StageService())

    def _run_to_completion(self, orchestrator: RunOrchestrator, run_id: str):
        run = orchestrator.get_run(run_id)
        assert run is not None
        guard = 0
        while run.state.value not in {"MEMORY_UPDATED", "REPORT_GENERATED"} and guard < 50:
            if run.state.value == "AWAITING_HUMAN_APPROVAL":
                run = orchestrator.approve(run_id, approved=True, approved_by="test", notes="")
                self.assertIsNotNone(run)
            else:
                run = orchestrator.advance(run_id)
                self.assertIsNotNone(run)
            guard += 1
        self.assertIsNotNone(run)
        self.assertEqual(run.state.value, "MEMORY_UPDATED")
        return run

    def test_chemistry_prompt_uses_chemistry_plugin_and_normalized_outputs(self):
        orch = self._orchestrator()
        run = orch.create_run(
            run_id="RUN-TEST-CHEM",
            user_goal="Optimize ionic conductivity for solid electrolytes while preserving phase stability",
        )
        run = orch.advance(run.run_id)  # compile-ir
        self.assertIsNotNone(run)
        ir = (run.artifacts.get("experiment_ir") or {})
        plugin = ((ir.get("plugin") or {}).get("selected_plugin"))
        self.assertEqual(plugin, "chemistry_materials")
        self.assertTrue((ir.get("ir_validation") or {}).get("is_valid"))

        final = self._run_to_completion(orch, run.run_id)
        norm = final.artifacts.get("normalized_results") or {}
        self.assertGreater(len(norm.get("observations") or []), 0)
        self.assertGreater(len(norm.get("series") or []), 0)
        self.assertGreater(len(norm.get("procedure_trace") or []), 0)

    def test_generic_prompt_falls_back_and_still_emits_observable_artifacts(self):
        orch = self._orchestrator()
        run = orch.create_run(
            run_id="RUN-TEST-GEN",
            user_goal="Optimize online ad placement strategy to maximize weekly conversion under budget constraints",
        )
        run = orch.advance(run.run_id)  # compile-ir
        self.assertIsNotNone(run)
        ir = (run.artifacts.get("experiment_ir") or {})
        plugin = ((ir.get("plugin") or {}).get("selected_plugin"))
        self.assertEqual(plugin, "generic_blackbox")
        self.assertTrue((ir.get("ir_validation") or {}).get("is_valid"))

        final = self._run_to_completion(orch, run.run_id)
        norm = final.artifacts.get("normalized_results") or {}
        self.assertGreater(len(norm.get("observations") or []), 0)
        self.assertGreater(len(norm.get("series") or []), 0)
        report = final.artifacts.get("report") or {}
        self.assertTrue("run_id" in report)

    def test_plugin_override_forces_generic_backend(self):
        orch = self._orchestrator()
        run = orch.create_run(
            run_id="RUN-TEST-OVERRIDE",
            user_goal="Optimize ionic conductivity for solid electrolytes while preserving phase stability",
            plugin_override="generic_blackbox",
        )
        run = orch.advance(run.run_id)  # compile-ir
        self.assertIsNotNone(run)
        ir = (run.artifacts.get("experiment_ir") or {})
        plugin = ((ir.get("plugin") or {}).get("selected_plugin"))
        self.assertEqual(plugin, "generic_blackbox")


if __name__ == "__main__":
    unittest.main()
