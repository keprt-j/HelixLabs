from __future__ import annotations

import random
from typing import Any

from helixlabs.domain.models import ExperimentIR, RunRecord
from helixlabs.services.plugins.base import ExperimentPlugin


def _seed(run: RunRecord) -> int:
    return abs(hash((run.run_id, run.user_goal))) % (2**31)


class GenericBlackBoxPlugin(ExperimentPlugin):
    plugin_id = "generic_blackbox"

    def can_handle(self, run: RunRecord) -> float:
        return 0.35

    def compile_ir(self, run: RunRecord) -> dict[str, Any]:
        rng = random.Random(_seed(run))
        n_points = 24
        design = [{"x1": round(i / 23, 4), "x2": round(rng.random(), 4)} for i in range(n_points)]
        ir = ExperimentIR(
            version="1.0",
            domain_hint="generic",
            hypothesis={
                "statement": run.pipeline.intake.claim_graph.get("main_claim")
                or "Unknown response may improve in a bounded region of the factor space.",
                "confidence": 0.35,
                "source_refs": [],
            },
            factors=[
                {"name": "x1", "type": "continuous", "bounds": {"min": 0.0, "max": 1.0}, "levels": [0.0, 0.25, 0.5, 0.75, 1.0]},
                {"name": "x2", "type": "continuous", "bounds": {"min": 0.0, "max": 1.0}, "levels": [0.0, 0.25, 0.5, 0.75, 1.0]},
            ],
            responses=[{"name": "objective_score", "objective": "maximize"}],
            constraints=[{"expression": "0 <= x1 <= 1 and 0 <= x2 <= 1", "severity": "hard"}],
            design={"strategy": "latin_hypercube_like", "sample_budget": n_points, "replicates": 1, "random_seed": _seed(run), "noise_model": "gaussian"},
            procedure_steps=[
                {"id": "sample", "name": "sample design points", "expected_outputs": ["design_points"]},
                {"id": "evaluate", "name": "evaluate black-box objective", "expected_outputs": ["observations"]},
                {"id": "rank", "name": "rank best candidates", "expected_outputs": ["top_candidates"]},
            ],
            analysis_plan={"primary_method": "blackbox_surface_scan"},
            provenance_refs=[],
        )
        return {
            "plugin_id": self.plugin_id,
            "design_matrix": design,
            "experiment_ir": ir.model_dump(),
            "simulation": {
                "version": 1,
                "seed": _seed(run),
                "fidelity": "low",
                "note": "Generic fallback plugin used due to low domain match confidence.",
            },
            "literature_fingerprint": {"mean_relevance": 0.0, "n_studies": 0, "top_tokens": []},
        }

    def validate_feasibility(self, run: RunRecord, experiment_ir_artifact: dict[str, Any]) -> dict[str, Any]:
        n = len(experiment_ir_artifact.get("design_matrix") or [])
        return {
            "validation_status": "passed_with_warnings",
            "issues": [
                "Generic plugin selected; results are low-fidelity black-box estimates.",
            ],
            "design_points": n,
        }

    def score_value(self, run: RunRecord, experiment_ir_artifact: dict[str, Any]) -> dict[str, Any]:
        return {
            "redundancy_score": 5.0,
            "novelty_score": 6.0,
            "expected_information_gain": 0.62,
            "overall_experiment_value": 0.58,
            "plugin_fidelity": "low",
        }

    def generate_protocol(self, run: RunRecord, experiment_ir_artifact: dict[str, Any]) -> dict[str, Any]:
        n = len(experiment_ir_artifact.get("design_matrix") or [])
        return {
            "protocol_id": f"P-{run.run_id}",
            "steps": ["sample_space", "evaluate_blackbox", "rank_candidates", "report"],
            "design_space": {"n_points": n, "axes": ["x1", "x2"]},
        }

    def schedule(self, run: RunRecord, experiment_ir_artifact: dict[str, Any]) -> dict[str, Any]:
        n = len(experiment_ir_artifact.get("design_matrix") or [])
        return {
            "schedule_id": f"SCH-{run.run_id}",
            "total_duration_hours": round(2.0 + n * 0.06, 2),
            "resource_utilization_pct": 54,
            "idle_time_hours": 1.3,
            "design_points": n,
            "hours_per_design_point": 0.06,
        }

    def execute(self, run: RunRecord, experiment_ir_artifact: dict[str, Any]) -> dict[str, Any]:
        rng = random.Random(_seed(run))
        design = list(experiment_ir_artifact.get("design_matrix") or [])
        measurements = []
        for i, d in enumerate(design):
            x1 = float(d.get("x1", 0.0))
            x2 = float(d.get("x2", 0.0))
            score = max(0.0, min(1.0, 0.8 - ((x1 - 0.62) ** 2 + (x2 - 0.38) ** 2) + rng.gauss(0, 0.03)))
            measurements.append({"design_index": i, "x1": x1, "x2": x2, "objective_score": round(score, 6)})
        by_x1 = sorted(measurements, key=lambda m: m["x1"])
        series = {
            "label": "Objective score vs x1",
            "x": [round(m["x1"], 4) for m in by_x1],
            "y": [m["objective_score"] for m in by_x1],
            "x_label": "x1",
            "y_label": "objective_score",
        }
        return {
            "status": "completed",
            "current_step": len(measurements),
            "total_steps": len(measurements),
            "simulation_config": experiment_ir_artifact.get("simulation", {}),
            "measurements": measurements,
            "series_for_charts": [series],
            "recovery_hint": None,
            "plugin_fidelity": "low",
        }

    def recover(self, run: RunRecord, execution_log: dict[str, Any]) -> dict[str, Any]:
        return {"selected_recovery": "none", "status": "not_required", "notes": "No explicit failure path in generic fallback."}

    def validate_results(self, run: RunRecord, execution_log: dict[str, Any]) -> dict[str, Any]:
        n = len(execution_log.get("measurements") or [])
        return {
            "validation_status": "repaired" if n else "skipped",
            "mapped_columns": {"x1": "factor_1", "x2": "factor_2", "objective_score": "response"},
            "validated_records": n,
        }

    def interpret(self, run: RunRecord, execution_log: dict[str, Any]) -> dict[str, Any]:
        m = list(execution_log.get("measurements") or [])
        if not m:
            return {"inference": "No measurements available.", "uncertainty": "n/a"}
        best = max(m, key=lambda x: float(x.get("objective_score", 0.0)))
        return {
            "best_condition": {"x1": best.get("x1"), "x2": best.get("x2"), "objective_score": best.get("objective_score")},
            "inference": "Generic black-box sweep found a candidate optimum in normalized factor space.",
            "uncertainty": "Low-fidelity fallback model; validate with domain-specific executor when available.",
        }

    def recommend_next(self, run: RunRecord, execution_log: dict[str, Any]) -> dict[str, Any]:
        m = list(execution_log.get("measurements") or [])
        if not m:
            return {"recommendation": "Increase sample budget and rerun generic sweep.", "expected_information_gain": 0.3, "risk_level": 0.5}
        best = max(m, key=lambda x: float(x.get("objective_score", 0.0)))
        return {
            "recommendation": f"Refine search near x1={best.get('x1')}, x2={best.get('x2')} with denser local sampling.",
            "expected_information_gain": 0.55,
            "risk_level": 0.42,
        }

    def report(self, run: RunRecord, execution_log: dict[str, Any], interpretation: dict[str, Any]) -> dict[str, Any]:
        n = len(execution_log.get("measurements") or [])
        return {
            "title": "HelixLabs report (generic black-box fallback)",
            "summary": interpretation.get("inference", ""),
            "run_id": run.run_id,
            "n_measurements": n,
            "plugin_fidelity": "low",
        }
