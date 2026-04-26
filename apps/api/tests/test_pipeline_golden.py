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


class StaticDisplayText:
    def polish_claim_graph(self, *, run, claim_graph, context):  # type: ignore[no-untyped-def]
        return {
            "display_main_claim": "Readable main claim for dashboard review.",
            "display_weakest_claim": "Readable weakest claim focused on boundary risk.",
            "display_next_target": "Readable next target for the experiment compiler.",
            "display_hypotheses": [
                {
                    "id": str(h.get("id")),
                    "title": f"Readable {h.get('title')}",
                    "statement": f"Readable statement for {h.get('id')}",
                    "rationale": "Stubbed readability rationale.",
                }
                for h in list(claim_graph.get("hypotheses") or [])
                if isinstance(h, dict)
            ],
        }

    def summarize_pipeline_section(self, *, run, section, section_json):  # type: ignore[no-untyped-def]
        return {
            "summary": f"{section} summary for judges.",
            "generated_at": "2026-01-01T00:00:00+00:00",
            "source": "stub",
        }

    def summarize_json_artifact(self, *, run, artifact_name, artifact_json):  # type: ignore[no-untyped-def]
        return {
            "summary": f"{artifact_name} artifact summary for judges.",
            "generated_at": "2026-01-01T00:00:00+00:00",
            "source": "stub",
        }


class PipelineGoldenTests(unittest.TestCase):
    def _orchestrator(self) -> RunOrchestrator:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        runtime = Path(tmp.name)
        repo = JsonRunRepository(runtime_dir=runtime)
        stage = StageService(
            synthesizer=LiteratureSynthesizerService(retriever=StaticRetriever()),
            evidence_store=EvidenceStore(store_dir=runtime / "evidence"),
            display_text=StaticDisplayText(),
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
        self.assertIn("main_claim", claim_graph)
        self.assertEqual(claim_graph.get("display_main_claim"), "Readable main claim for dashboard review.")
        self.assertEqual(len(claim_graph.get("display_hypotheses") or []), 3)

        final = self._run_to_completion(orch, run.run_id)
        summaries = final.artifacts.get("pipeline_summaries") or {}
        self.assertEqual((summaries.get("planning") or {}).get("summary"), "planning summary for judges.")
        self.assertEqual((summaries.get("runtime") or {}).get("summary"), "runtime summary for judges.")
        self.assertEqual((summaries.get("outcomes") or {}).get("summary"), "outcomes summary for judges.")
        artifact_summaries = final.artifacts.get("artifact_summaries") or {}
        for key in [
            "experiment_ir",
            "feasibility_report",
            "value_score",
            "protocol",
            "schedule",
            "execution_log",
            "failure_recovery_plan",
            "validation_report",
            "interpretation",
            "next_experiment_recommendation",
            "memory_update",
            "report",
        ]:
            self.assertEqual(
                (artifact_summaries.get(key) or {}).get("summary"),
                f"{key} artifact summary for judges.",
            )
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

    def test_non_chemistry_prompt_uses_adaptive_universal_and_emits_observable_artifacts(self):
        orch = self._orchestrator()
        run = orch.create_run(
            run_id="RUN-TEST-GEN",
            user_goal="Optimize online ad placement strategy to maximize weekly conversion under budget constraints",
        )
        run = orch.advance(run.run_id)  # compile-ir
        self.assertIsNotNone(run)
        ir = (run.artifacts.get("experiment_ir") or {})
        plugin = ((ir.get("plugin") or {}).get("selected_plugin"))
        self.assertEqual(plugin, "adaptive_universal")
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
        selected_stmt = replanned.pipeline.intake.claim_graph.get("selected_hypothesis_display_statement")
        self.assertEqual(target_claim, selected_stmt)

    def test_pipeline_summaries_are_created_at_section_boundaries(self):
        orch = self._orchestrator()
        run = orch.create_run(
            run_id="RUN-TEST-SUMMARY-STAGES",
            user_goal="Tune sintering temperature and dwell time to improve cathode conductivity without increasing crack risk",
        )
        self.assertNotIn("pipeline_summaries", run.artifacts)

        for _ in range(5):
            run = orch.advance(run.run_id)
            self.assertIsNotNone(run)
        summaries = run.artifacts.get("pipeline_summaries") or {}
        self.assertIn("planning", summaries)
        self.assertNotIn("runtime", summaries)
        self.assertNotIn("outcomes", summaries)
        artifact_summaries = run.artifacts.get("artifact_summaries") or {}
        for key in ["experiment_ir", "feasibility_report", "value_score", "protocol", "schedule"]:
            self.assertIn(key, artifact_summaries)

        run = orch.approve(run.run_id, approved=True, approved_by="test", notes="")
        self.assertIsNotNone(run)
        for _ in range(4):
            run = orch.advance(run.run_id)
            self.assertIsNotNone(run)
        summaries = run.artifacts.get("pipeline_summaries") or {}
        self.assertIn("runtime", summaries)
        self.assertNotIn("outcomes", summaries)
        artifact_summaries = run.artifacts.get("artifact_summaries") or {}
        for key in ["execution_log", "failure_recovery_plan", "validation_report", "interpretation"]:
            self.assertIn(key, artifact_summaries)

        for _ in range(2):
            run = orch.advance(run.run_id)
            self.assertIsNotNone(run)
        summaries = run.artifacts.get("pipeline_summaries") or {}
        self.assertIn("outcomes", summaries)
        artifact_summaries = run.artifacts.get("artifact_summaries") or {}
        for key in ["next_experiment_recommendation", "memory_update", "report"]:
            self.assertIn(key, artifact_summaries)

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

    def test_biomedical_goal_avoids_physical_axis_hallucinations(self):
        orch = self._orchestrator()
        run = orch.create_run(
            run_id="RUN-TEST-BIO",
            user_goal="Investigate OGG1 in Alzheimer's disease progression",
        )
        run = orch.advance(run.run_id)  # compile-ir
        self.assertIsNotNone(run)
        ir = (run.artifacts.get("experiment_ir") or {})
        plugin = ((ir.get("plugin") or {}).get("selected_plugin"))
        self.assertEqual(plugin, "adaptive_universal")
        final = self._run_to_completion(orch, run.run_id)
        execution = final.artifacts.get("execution_log") or {}
        series = list(execution.get("series_for_charts") or [])
        self.assertGreater(len(series), 0)
        first = series[0] if isinstance(series[0], dict) else {}
        x_label = str(first.get("x_label", "")).lower()
        x_unit = str(first.get("x_unit", "")).lower()
        self.assertNotIn("voltage", x_label)
        self.assertNotIn(x_unit, {"v", "kpa", "c"})

    def test_biomedical_hypothesis_is_not_token_list(self):
        orch = self._orchestrator()
        run = orch.create_run(
            run_id="RUN-TEST-BIO-CLAIM",
            user_goal="Investigate OGG1 in Alzheimer's disease progression",
        )
        claim_graph = run.pipeline.intake.claim_graph or {}
        main_claim = str(claim_graph.get("main_claim") or "").lower()
        self.assertIn("ogg1", main_claim)
        self.assertNotIn("investigate, ogg1", main_claim)
        self.assertNotIn("strongly influences the target outcome", main_claim)


if __name__ == "__main__":
    unittest.main()
