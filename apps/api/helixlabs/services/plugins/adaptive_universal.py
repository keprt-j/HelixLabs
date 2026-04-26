from __future__ import annotations

import random
import re
from typing import Any

from helixlabs.domain.models import ExperimentIR, RunRecord
from helixlabs.services.plugins.base import ExperimentPlugin
from helixlabs.services.pipeline_simulation import measurement_distribution_scores


def _seed(run: RunRecord) -> int:
    return abs(hash((run.run_id, run.user_goal, "adaptive_universal"))) % (2**31)


def _sim_overrides(run: RunRecord) -> dict[str, Any]:
    v = run.artifacts.get("simulation_overrides")
    return v if isinstance(v, dict) else {}


def _sample_budget(run: RunRecord) -> int:
    density = str(_sim_overrides(run).get("design_density", "medium")).lower()
    if density == "coarse":
        return 18
    if density == "fine":
        return 42
    return 28


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


def _entities(run: RunRecord) -> list[str]:
    parsed = run.pipeline.intake.parsed_goal or {}
    raw = parsed.get("entities")
    if isinstance(raw, list):
        return [str(v).strip() for v in raw if str(v).strip()]
    return []


def _slug(name: str, fallback: str) -> str:
    tokens = re.findall(r"[a-zA-Z0-9]+", name.lower())
    if not tokens:
        return fallback
    return "_".join(tokens[:3])


def _goal_requests_physical_axes(run: RunRecord) -> bool:
    g = run.user_goal.lower()
    return any(
        term in g
        for term in (
            "temperature",
            "thermal",
            "pressure",
            "voltage",
            "current density",
            "concentration",
            "mol%",
            "dwell",
            "duration",
            "time",
        )
    )


def _sanitize_hints_for_domain(run: RunRecord, hints: dict[str, str], entities: list[str]) -> dict[str, str]:
    out = dict(hints)
    domain = str((run.pipeline.intake.parsed_goal or {}).get("domain") or "")
    if domain != "biomedical_research" or _goal_requests_physical_axes(run):
        return out
    physical_labels = {"temperature", "time", "pressure", "voltage", "current density", "concentration"}
    physical_units = {"c", "h", "kpa", "v", "mol%", "ma/cm2"}
    x_label = str(out.get("x_label") or "").strip().lower()
    x_unit = str(out.get("x_unit") or "").strip().lower()
    y_label = str(out.get("y_label") or "").strip().lower()
    y_unit = str(out.get("y_unit") or "").strip().lower()
    if x_label in physical_labels or x_unit in physical_units:
        out["x_label"] = entities[0] if entities else "Biological Variable"
        out["x_unit"] = ""
    if y_label in {"conductivity", "capacity", "strength", "cost"} or y_unit in {"s/cm", "mah/g", "mpa", "usd"}:
        out["y_label"] = "Clinical outcome"
        out["y_unit"] = "score"
        out["y_format"] = "float"
    return out


class AdaptiveUniversalPlugin(ExperimentPlugin):
    plugin_id = "adaptive_universal"

    def can_handle(self, run: RunRecord) -> float:
        text = run.user_goal.lower()
        chemistry_markers = (
            "electrolyte",
            "conductivity",
            "cathode",
            "anode",
            "sinter",
            "dwell",
            "calcine",
            "anneal",
            "phase",
            "battery",
            "materials",
            "dop",
            "oxide",
            "ceramic",
        )
        if any(marker in text for marker in chemistry_markers):
            # Defer to the chemistry plugin when a clear domain match exists.
            return 0.35
        entities = _entities(run)
        hints = _axis_hints(run)
        studies = list((run.pipeline.intake.literature or {}).get("studies") or [])
        score = 0.62
        if len(entities) >= 2:
            score += 0.07
        if hints.get("x_label") or hints.get("y_label"):
            score += 0.06
        if studies:
            score += min(0.12, len(studies) * 0.02)
        if any(k in text for k in ("optimize", "maximize", "minimize", "improve", "investigate", "evaluate")):
            score += 0.05
        return max(0.0, min(0.95, score))

    def compile_ir(self, run: RunRecord) -> dict[str, Any]:
        rng = random.Random(_seed(run))
        n_points = _sample_budget(run)
        denom = max(1, n_points - 1)
        design = [{"u1": round(i / denom, 4), "u2": round(rng.random(), 4)} for i in range(n_points)]

        entities = _entities(run)
        hints = _sanitize_hints_for_domain(run, _axis_hints(run), entities)
        x_label = str(hints.get("x_label") or (entities[0] if entities else "Primary Variable"))
        y_label = str(hints.get("y_label") or "Target Response")
        x_unit = str(hints.get("x_unit") or "")
        y_unit = str(hints.get("y_unit") or "")
        y_key = _slug(y_label, "target_response")
        f1_name = _slug(x_label, "primary_variable")
        f2_source = entities[1] if len(entities) > 1 else "secondary_factor"
        f2_name = _slug(f2_source, "secondary_factor")
        domain_hint = str((run.pipeline.intake.parsed_goal or {}).get("domain") or "general_experimentation")

        ir = ExperimentIR(
            version="1.0",
            domain_hint=domain_hint,
            hypothesis={
                "statement": run.pipeline.intake.claim_graph.get("main_claim")
                or "Evidence suggests a measurable relationship exists between controllable variables and the target response.",
                "confidence": 0.55,
                "source_refs": [],
            },
            factors=[
                {
                    "name": f1_name,
                    "type": "continuous",
                    "units": x_unit or None,
                    "bounds": {"min": 0.0, "max": 1.0},
                    "levels": [0.0, 0.25, 0.5, 0.75, 1.0],
                },
                {
                    "name": f2_name,
                    "type": "continuous",
                    "bounds": {"min": 0.0, "max": 1.0},
                    "levels": [0.0, 0.25, 0.5, 0.75, 1.0],
                },
            ],
            responses=[{"name": y_key, "objective": "maximize", "units": y_unit or None}],
            constraints=[
                {
                    "expression": f"0 <= {f1_name} <= 1 and 0 <= {f2_name} <= 1",
                    "severity": "hard",
                }
            ],
            design={
                "strategy": "evidence_conditioned_surface_scan",
                "sample_budget": n_points,
                "replicates": _replicates(run),
                "random_seed": _seed(run),
                "noise_model": "gaussian",
            },
            procedure_steps=[
                {"id": "extract", "name": "extract evidence-grounded variables", "expected_outputs": ["factor_map"]},
                {"id": "sample", "name": "sample design points", "expected_outputs": ["design_points"]},
                {"id": "evaluate", "name": "evaluate objective response", "expected_outputs": ["observations"]},
                {"id": "rank", "name": "rank top candidates", "expected_outputs": ["ranked_candidates"]},
            ],
            analysis_plan={"primary_method": "response_surface_scan"},
            provenance_refs=[],
        )
        return {
            "plugin_id": self.plugin_id,
            "design_matrix": design,
            "experiment_ir": ir.model_dump(),
            "simulation": {
                "version": 1,
                "seed": _seed(run),
                "fidelity": "medium",
                "note": "Evidence-conditioned universal simulator selected for non-chemistry domains.",
            },
            "literature_fingerprint": {
                "n_studies": len(list((run.pipeline.intake.literature or {}).get("studies") or [])),
                "top_tokens": entities[:8],
            },
        }

    def validate_feasibility(self, run: RunRecord, experiment_ir_artifact: dict[str, Any]) -> dict[str, Any]:
        n = len(experiment_ir_artifact.get("design_matrix") or [])
        return {
            "validation_status": "passed_with_warnings",
            "issues": [
                "Universal plugin uses evidence-conditioned simulation and should be followed by domain-specific validation.",
            ],
            "design_points": n,
        }

    def score_value(self, run: RunRecord, experiment_ir_artifact: dict[str, Any]) -> dict[str, Any]:
        n = len(experiment_ir_artifact.get("design_matrix") or [])
        rep = _replicates(run)
        novelty = max(2.5, min(9.2, 8.4 - n / 14.0))
        eig = max(0.3, min(0.92, 0.4 + (n / 56.0) + (rep - 1) * 0.05))
        overall = max(0.35, min(0.92, 0.5 + eig * 0.32))
        return {
            "redundancy_score": round(10.0 - novelty, 2),
            "novelty_score": round(novelty, 2),
            "expected_information_gain": round(eig, 3),
            "overall_experiment_value": round(overall, 3),
            "plugin_fidelity": "medium",
        }

    def generate_protocol(self, run: RunRecord, experiment_ir_artifact: dict[str, Any]) -> dict[str, Any]:
        n = len(experiment_ir_artifact.get("design_matrix") or [])
        return {
            "protocol_id": f"P-{run.run_id}",
            "steps": ["extract_variables", "sample_space", "evaluate_response", "rank_candidates", "report"],
            "design_space": {"n_points": n, "axes": ["u1", "u2"]},
        }

    def schedule(self, run: RunRecord, experiment_ir_artifact: dict[str, Any]) -> dict[str, Any]:
        n = len(experiment_ir_artifact.get("design_matrix") or [])
        rep = _replicates(run)
        noise = float(_sim_overrides(run).get("noise_scale_relative", 0.06))
        hours_per = 0.05 + rep * 0.026 + noise * 0.12
        total = round(1.5 + n * hours_per, 2)
        util = min(92, round(48 + n / 2))
        idle = round(max(0.7, total * 0.14), 2)
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
            u1 = float(d.get("u1", 0.0))
            u2 = float(d.get("u2", 0.0))
            score = max(0.0, min(1.0, 0.84 - ((u1 - 0.58) ** 2 + (u2 - 0.41) ** 2) + rng.gauss(0, 0.028)))
            measurements.append({"design_index": i, "u1": u1, "u2": u2, "objective_score": round(score, 6)})

        by_u1 = sorted(measurements, key=lambda m: m["u1"])
        entities = _entities(run)
        hints = _sanitize_hints_for_domain(run, _axis_hints(run), entities)
        x_label = str(hints.get("x_label") or (entities[0] if entities else "Primary Variable"))
        y_label = str(hints.get("y_label") or "Target Response")
        x_unit = str(hints.get("x_unit") or "")
        y_unit = str(hints.get("y_unit") or "")
        y_format = str(hints.get("y_format") or "float")

        series = {
            "label": f"{y_label} vs {x_label}",
            "x": [round(m["u1"], 4) for m in by_u1],
            "y": [m["objective_score"] for m in by_u1],
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
            "plugin_fidelity": "medium",
            "origin": "simulated",
        }

    def recover(self, run: RunRecord, execution_log: dict[str, Any]) -> dict[str, Any]:
        return {
            "selected_recovery": "none",
            "status": "not_required",
            "notes": "No explicit failure path triggered in adaptive universal simulation.",
        }

    def validate_results(self, run: RunRecord, execution_log: dict[str, Any]) -> dict[str, Any]:
        n = len(execution_log.get("measurements") or [])
        return {
            "validation_status": "repaired" if n else "skipped",
            "mapped_columns": {"u1": "primary_variable", "u2": "secondary_variable", "objective_score": "target_response"},
            "validated_records": n,
        }

    def interpret(self, run: RunRecord, execution_log: dict[str, Any]) -> dict[str, Any]:
        m = list(execution_log.get("measurements") or [])
        if not m:
            return {"inference": "No measurements available.", "uncertainty": "n/a"}
        best = max(m, key=lambda x: float(x.get("objective_score", 0.0)))
        return {
            "best_condition": {"u1": best.get("u1"), "u2": best.get("u2"), "objective_score": best.get("objective_score")},
            "inference": "Evidence-conditioned universal scan found a candidate optimum in adaptive factor space.",
            "uncertainty": "Simulation-guided result; validate with domain-specific data before deployment.",
        }

    def recommend_next(self, run: RunRecord, execution_log: dict[str, Any]) -> dict[str, Any]:
        m = list(execution_log.get("measurements") or [])
        hints = _axis_hints(run)
        x_label = str(hints.get("x_label") or "primary variable")
        if not m:
            scores = measurement_distribution_scores([])
            return {
                "recommendation": "Increase sample budget and rerun with stronger evidence constraints.",
                "expected_information_gain": scores["expected_information_gain"],
                "risk_level": scores["risk_level"],
                "score_basis": scores["score_basis"],
            }
        best = max(m, key=lambda x: float(x.get("objective_score", 0.0)))
        scores = measurement_distribution_scores(
            m,
            response_keys=["objective_score"],
            axis_keys=["u1", "u2"],
        )
        return {
            "recommendation": (
                f"Refine search near {x_label}={best.get('u1')} and run local sensitivity analysis around the candidate optimum."
            ),
            "expected_information_gain": scores["expected_information_gain"],
            "risk_level": scores["risk_level"],
            "score_basis": scores["score_basis"],
        }

    def report(self, run: RunRecord, execution_log: dict[str, Any], interpretation: dict[str, Any]) -> dict[str, Any]:
        n = len(execution_log.get("measurements") or [])
        return {
            "title": "HelixLabs report (adaptive universal simulation)",
            "summary": interpretation.get("inference", ""),
            "scope_note": (
                "Evidence-conditioned simulation for planning support across domains; not a protocol-faithful "
                "replication of any individual source study."
            ),
            "run_id": run.run_id,
            "n_measurements": n,
            "plugin_fidelity": "medium",
        }
