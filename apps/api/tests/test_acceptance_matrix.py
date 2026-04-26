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
                "title": "Static study one",
                "authors": "A. Tester",
                "year": 2024,
                "doi": "10.0000/acc-static-1",
                "url": "https://example.org/acc-static-1",
                "source": "static",
                "abstract": "Objective factors correlate with response under bounded constraints in controlled tests.",
                "exists": True,
            },
            {
                "title": "Static study two",
                "authors": "B. Tester",
                "year": 2023,
                "doi": "10.0000/acc-static-2",
                "url": "https://example.org/acc-static-2",
                "source": "static",
                "abstract": "Response variation depends on interventions and operating windows across practical settings.",
                "exists": True,
            },
        ]
        return base[: max(1, min(limit, len(base)))]


class AcceptanceMatrixTests(unittest.TestCase):
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
