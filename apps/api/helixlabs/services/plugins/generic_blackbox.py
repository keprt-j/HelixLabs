from __future__ import annotations

import random
import re
from typing import Any

from helixlabs.domain.models import ExperimentIR, RunRecord
from helixlabs.services.plugins.base import ExperimentPlugin
from helixlabs.services.pipeline_simulation import measurement_distribution_scores


def _seed(run: RunRecord) -> int:
    return abs(hash((run.run_id, run.user_goal))) % (2**31)


def _sim_overrides(run: RunRecord) -> dict[str, Any]:
    v = run.artifacts.get("simulation_overrides")
    return v if isinstance(v, dict) else {}


def _sample_budget(run: RunRecord) -> int:
    density = str(_sim_overrides(run).get("design_density", "medium")).lower()
    if density == "coarse":
        return 16
    if density == "fine":
        return 40
    return 24


def _replicates(run: RunRecord) -> int:
    raw = _sim_overrides(run).get("n_replicates", 1)
    try:
        return max(1, min(20, int(raw)))
    except (TypeError, ValueError):
        return 1


def _axis_hints(run: RunRecord) -> dict[str, str]:
    lit = run.pipeline.intake.literature or {}
    hints = lit.get("axis_hints")
    return hints if isinstance(hints, dict) else {}


def _slug(name: str, fallback: str) -> str:
    tokens = re.findall(r"[a-zA-Z0-9]+", name.lower())
    if not tokens:
        return fallback
    return "_".join(tokens[:3])


def _x_bounds(run: RunRecord, hints: dict[str, str]) -> tuple[float, float] | None:
    unit = str(hints.get("x_unit") or "").strip().lower()
    label = str(hints.get("x_label") or "").strip().lower()
    goal = run.user_goal.lower()
    if unit == "c":
        if any(k in goal for k in ("sinter", "calcine", "anneal", "firing")):
            return 650.0, 950.0
        return 20.0, 450.0
    if unit == "h":
        return 0.5, 24.0
    if unit == "kpa":
        return 50.0, 500.0
    if unit == "v":
        return 0.5, 5.0
    if unit == "mol%":
        return 0.1, 10.0
    if "temperature" in label:
        if any(k in goal for k in ("sinter", "calcine", "anneal", "firing")):
            return 650.0, 950.0
        return 20.0, 450.0
    if "time" in label or "dwell" in label:
        return 0.5, 24.0
    return None


class GenericBlackBoxPlugin(ExperimentPlugin):
    plugin_id = "generic_blackbox"

    def can_handle(self, run: RunRecord) -> float:
        return 0.4

    def compile_ir(self, run: RunRecord) -> dict[str, Any]:
        rng = random.Random(_seed(run))
        n_points = _sample_budget(run)
        denom = max(1, n_points - 1)
        design = [{"x1": round(i / denom, 4), "x2": round(rng.random(), 4)} for i in range(n_points)]
        hints = _axis_hints(run)
        x_label = str(hints.get("x_label") or "Input Variable")
        y_label = str(hints.get("y_label") or "Response")
        x_unit = str(hints.get("x_unit") or "")
        y_unit = str(hints.get("y_unit") or "")
        y_key = _slug(y_label, "response_metric")
        x_bounds = _x_bounds(run, hints)
        if x_unit and x_bounds is None:
            # Guardrail: do not expose a physical unit when the x-axis remains normalized.
            x_label = "Normalized Input Variable"
            x_unit = ""
        ir = ExperimentIR(
            version="1.0",
            domain_hint="generic",
            hypothesis={
                "statement": run.pipeline.intake.claim_graph.get("main_claim")
                or "Unknown response may improve in a bounded region of the factor space.",
                "confidence": 0.42,
                "source_refs": [],
            },
            factors=[
                {
                    "name": _slug(x_label, "x1"),
                    "type": "continuous",
                    "units": x_unit or None,
                    "bounds": {"min": x_bounds[0], "max": x_bounds[1]} if x_bounds else {"min": 0.0, "max": 1.0},
                    "levels": [0.0, 0.25, 0.5, 0.75, 1.0],
                },
                {
                    "name": "auxiliary_factor",
                    "type": "continuous",
                    "bounds": {"min": 0.0, "max": 1.0},
                    "levels": [0.0, 0.25, 0.5, 0.75, 1.0],
                },
            ],
            responses=[{"name": y_key, "objective": "maximize", "units": y_unit or None}],
            constraints=[{"expression": "0 <= x1 <= 1 and 0 <= x2 <= 1", "severity": "hard"}],
            design={
                "strategy": "latin_hypercube_like",
                "sample_budget": n_points,
                "replicates": _replicates(run),
                "random_seed": _seed(run),
                "noise_model": "gaussian",
            },
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
                "x_bounds": {"min": x_bounds[0], "max": x_bounds[1]} if x_bounds else {"min": 0.0, "max": 1.0},
            },
            "literature_fingerprint": {
                "mean_relevance": float((run.pipeline.intake.prior_work or {}).get("novelty_score", 5.0)) / 10.0,
                "n_studies": len(list((run.pipeline.intake.literature or {}).get("studies") or [])),
                "top_tokens": list((run.pipeline.intake.parsed_goal or {}).get("entities") or [])[:6],
            },
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
        n = len(experiment_ir_artifact.get("design_matrix") or [])
        rep = _replicates(run)
        novelty = max(2.0, min(9.5, 8.0 - n / 12.0))
        eig = max(0.25, min(0.9, 0.35 + (n / 50.0) + (rep - 1) * 0.04))
        overall = max(0.3, min(0.9, 0.45 + eig * 0.35))
        return {
            "redundancy_score": round(10.0 - novelty, 2),
            "novelty_score": round(novelty, 2),
            "expected_information_gain": round(eig, 3),
            "overall_experiment_value": round(overall, 3),
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
        rep = _replicates(run)
        noise = float(_sim_overrides(run).get("noise_scale_relative", 0.06))
        hours_per = 0.04 + rep * 0.025 + noise * 0.1
        total = round(1.2 + n * hours_per, 2)
        util = min(90, round(45 + n / 2))
        idle = round(max(0.6, total * 0.15), 2)
        return {
            "schedule_id": f"SCH-{run.run_id}",
            "total_duration_hours": total,
            "resource_utilization_pct": util,
            "idle_time_hours": idle,
            "design_points": n,
            "hours_per_design_point": round(hours_per, 3),
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
        hints = _axis_hints(run)
        x_label = str(hints.get("x_label") or "Input Variable")
        y_label = str(hints.get("y_label") or "Response")
        x_unit = str(hints.get("x_unit") or "")
        y_unit = str(hints.get("y_unit") or "")
        y_format = str(hints.get("y_format") or "float")
        x_bounds = _x_bounds(run, hints)
        if x_unit and x_bounds is None:
            x_label = "Normalized Input Variable"
            x_unit = ""
        if x_bounds is not None:
            lo, hi = x_bounds
            span = max(1e-9, hi - lo)
            x_values = [round(lo + m["x1"] * span, 4) for m in by_x1]
        else:
            x_values = [round(m["x1"], 4) for m in by_x1]
        series = {
            "label": f"{y_label} vs {x_label}",
            "x": x_values,
            "y": [m["objective_score"] for m in by_x1],
            "x_label": x_label,
            "y_label": y_label,
            "x_unit": x_unit,
            "y_unit": y_unit,
            "y_format": y_format,
            "x_key": "x",
            "y_key": "y",
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
            "origin": "simulated",
        }

    def recover(self, run: RunRecord, execution_log: dict[str, Any]) -> dict[str, Any]:
        return {"selected_recovery": "none", "status": "not_required", "notes": "No explicit failure path in generic fallback."}

    def validate_results(self, run: RunRecord, execution_log: dict[str, Any]) -> dict[str, Any]:
        n = len(execution_log.get("measurements") or [])
        hints = _axis_hints(run)
        x_label = _slug(str(hints.get("x_label") or "x"), "x")
        y_label = _slug(str(hints.get("y_label") or "response"), "response")
        return {
            "validation_status": "repaired" if n else "skipped",
            "mapped_columns": {"x1": x_label, "x2": "auxiliary_factor", "objective_score": y_label},
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
        hints = _axis_hints(run)
        x_label = str(hints.get("x_label") or "primary variable")
        if not m:
            scores = measurement_distribution_scores([])
            return {
                "recommendation": "Increase sample budget and rerun generic sweep.",
                "expected_information_gain": scores["expected_information_gain"],
                "risk_level": scores["risk_level"],
                "score_basis": scores["score_basis"],
            }
        best = max(m, key=lambda x: float(x.get("objective_score", 0.0)))
        scores = measurement_distribution_scores(
            m,
            response_keys=["objective_score"],
            axis_keys=["x1", "x2"],
        )
        return {
            "recommendation": f"Refine search near {x_label}={best.get('x1')} with denser local sampling and local sensitivity checks.",
            "expected_information_gain": scores["expected_information_gain"],
            "risk_level": scores["risk_level"],
            "score_basis": scores["score_basis"],
        }

    def report(self, run: RunRecord, execution_log: dict[str, Any], interpretation: dict[str, Any]) -> dict[str, Any]:
        n = len(execution_log.get("measurements") or [])
        return {
            "title": "HelixLabs report (generic black-box fallback)",
            "summary": interpretation.get("inference", ""),
            "scope_note": (
                "Evidence-conditioned low-fidelity simulation for planning support; not a protocol-faithful "
                "replication of any individual source study."
            ),
            "run_id": run.run_id,
            "n_measurements": n,
            "plugin_fidelity": "low",
        }
