from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from helixlabs.repos.json_run_repository import JsonRunRepository
from helixlabs.services.evidence_store import EvidenceStore
from helixlabs.services.literature_retriever import LiteratureRetrieverService
from helixlabs.services.literature_synthesizer import LiteratureSynthesizerService
from helixlabs.services.orchestrator import RunOrchestrator
from helixlabs.services.stage_service import StageService


class StaticRetriever(LiteratureRetrieverService):
    def retrieve(self, query: str, limit: int = 200, time_budget_s: float = 4.0):  # type: ignore[override]
        base = [
            {
                "title": "Sintering-window tuning for cathode conductivity",
                "authors": "A. Doe, B. Kim",
                "year": 2024,
                "doi": "10.0000/static-1",
                "url": "https://example.org/static-1",
                "source": "static",
                "abstract": "Temperature and dwell time jointly influence conductivity and crack risk in sintered cathodes.",
                "exists": True,
            },
            {
                "title": "Dwell-time effects on microcrack suppression",
                "authors": "C. Lee",
                "year": 2023,
                "doi": "10.0000/static-2",
                "url": "https://example.org/static-2",
                "source": "static",
                "abstract": "Extended dwell can improve densification but excessive dwell increases crack susceptibility.",
                "exists": True,
            },
            {
                "title": "Impedance trends across thermal schedules",
                "authors": "R. Patel",
                "year": 2022,
                "doi": "10.0000/static-3",
                "url": "https://example.org/static-3",
                "source": "static",
                "abstract": "Conductivity response is non-linear across sintering temperature windows and hold durations.",
                "exists": True,
            },
        ]
        return base[: max(1, min(limit, len(base)))]


class PipelineGoldenTests(unittest.TestCase):
    def _orchestrator(self) -> RunOrchestrator:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        runtime = Path(tmp.name)
        repo = JsonRunRepository(runtime_dir=runtime)
        stage = StageService(
            synthesizer=LiteratureSynthesizerService(retriever=StaticRetriever()),
            evidence_store=EvidenceStore(store_dir=runtime / "evidence"),
        )
        return RunOrchestrator(repo=repo, stage_service=stage)

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
        literature = run.pipeline.intake.literature or {}
        self.assertIn("evidence_manifest", literature)
        self.assertGreaterEqual(int((literature.get("evidence_manifest") or {}).get("doc_count", 0)), 1)
        claim_graph = run.pipeline.intake.claim_graph or {}
        context = claim_graph.get("context") or {}
        self.assertIn("claim_evidence", context)

        final = self._run_to_completion(orch, run.run_id)
        norm = final.artifacts.get("normalized_results") or {}
        self.assertGreater(len(norm.get("observations") or []), 0)
        self.assertGreater(len(norm.get("series") or []), 0)
        self.assertGreater(len(norm.get("procedure_trace") or []), 0)
        ex = final.artifacts.get("execution_log") or {}
        measurements = list(ex.get("measurements") or [])
        series_list = list(ex.get("series_for_charts") or [])
        self.assertGreater(len(series_list), 0)
        series = series_list[0]
        temps = list(series.get("temperature_c") or [])
        sigmas = list(series.get("sigma_S_cm") or [])
        self.assertEqual(len(temps), len(sigmas))
        slice_factor = str(series.get("slice_factor", ""))
        if slice_factor == "dwell_time_h":
            target = float(series.get("slice_value", 0.0))
            expected = [m for m in measurements if abs(float(m.get("dwell_time_h", -999.0)) - target) < 1e-9]
            expected.sort(key=lambda m: float(m["temperature_c"]))
            self.assertEqual(len(expected), len(temps))
            for idx, m in enumerate(expected):
                self.assertAlmostEqual(float(temps[idx]), float(m["temperature_c"]), places=6)
                self.assertAlmostEqual(float(sigmas[idx]), float(m["sigma_S_cm_mean"]), places=6)

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
        evidence = orch.retrieve_evidence(
            run_id=final.run_id,
            query=final.user_goal,
            top_k=3,
        )
        self.assertGreater(len(evidence), 0)

    def test_user_hypothesis_selection_retargets_planning(self):
        orch = self._orchestrator()
        run = orch.create_run(
            run_id="RUN-TEST-SELECT",
            user_goal="Tune sintering temperature and dwell time to improve cathode conductivity without increasing crack risk",
        )
        cg = run.pipeline.intake.claim_graph or {}
        hyps = list(cg.get("hypotheses") or [])
        self.assertEqual(len(hyps), 3)
        selected = orch.select_hypothesis(run.run_id, "H3")
        self.assertIsNotNone(selected)
        self.assertEqual(selected.pipeline.intake.claim_graph.get("selected_hypothesis_id"), "H3")
        replanned = orch.replan(run.run_id)
        self.assertIsNotNone(replanned)
        target_claim = (replanned.artifacts.get("experiment_ir") or {}).get("target_claim")
        selected_stmt = replanned.pipeline.intake.claim_graph.get("selected_hypothesis_statement")
        self.assertEqual(target_claim, selected_stmt)

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
