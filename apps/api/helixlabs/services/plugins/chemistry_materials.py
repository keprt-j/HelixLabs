from __future__ import annotations

from typing import Any

from helixlabs.domain.models import ExperimentIR, RunRecord
from helixlabs.services.pipeline_simulation import (
    build_simulation_config,
    design_experiment_matrix,
    execution_payload,
    feasibility_from_literature_and_design,
    interpret_from_measurements,
    literature_fingerprint,
    protocol_from_design,
    recommend_next_from_measurements,
    recovery_payload,
    report_payload,
    run_measurements,
    schedule_from_design,
    validation_payload,
    value_scores_from_context,
)
from helixlabs.services.plugins.base import ExperimentPlugin


class ChemistryMaterialsPlugin(ExperimentPlugin):
    plugin_id = "chemistry_materials"

    def can_handle(self, run: RunRecord) -> float:
        text = run.user_goal.lower()
        keys = ["electrolyte", "conductivity", "dop", "phase", "materials", "battery", "chem"]
        hits = sum(1 for k in keys if k in text)
        if hits == 0:
            return 0.08
        if hits == 1:
            return 0.28
        return min(1.0, 0.18 + hits * 0.12)

    def compile_ir(self, run: RunRecord) -> dict[str, Any]:
        design, meta = design_experiment_matrix(run)
        fp = meta["fingerprint"]
        sim_cfg = build_simulation_config(run)
        fracs = sorted({float(p["fraction_mol_pct"]) for p in design}) or [0.0, 1.0]
        temps = sorted({float(p["temperature_c"]) for p in design}) or [20.0, 40.0]
        source_refs = [str(s.get("doi")) for s in list(run.pipeline.intake.literature.get("studies") or []) if s.get("doi")]
        ir = ExperimentIR(
            version="1.0",
            domain_hint="chemistry_materials",
            hypothesis={
                "statement": str(
                    run.pipeline.intake.claim_graph.get("main_claim")
                    or "Composition and operating conditions can improve target response."
                ),
                "confidence": max(0.05, min(0.95, float(fp.get("mean_relevance", 0.5)))),
                "source_refs": source_refs[:8],
            },
            factors=[
                {
                    "name": "fraction_mol_pct",
                    "type": "continuous",
                    "units": "mol%",
                    "bounds": {"min": min(fracs), "max": max(fracs)},
                    "levels": fracs,
                },
                {
                    "name": "temperature_c",
                    "type": "continuous",
                    "units": "C",
                    "bounds": {"min": min(temps), "max": max(temps)},
                    "levels": temps,
                },
            ],
            responses=[
                {"name": "conductivity", "objective": "maximize", "units": "S/cm"},
                {"name": "phase_proxy", "objective": "maximize"},
            ],
            constraints=[
                {"expression": "sample_budget >= replicates", "severity": "hard"},
            ],
            design={
                "strategy": "literature_conditioned_grid",
                "sample_budget": len(design),
                "replicates": max(1, int(sim_cfg.get("n_replicates", 1))),
                "random_seed": int(sim_cfg.get("seed", 0)),
                "noise_model": "lognormal_relative",
            },
            procedure_steps=[
                {"id": "prepare", "name": "prepare inputs", "expected_outputs": ["prepared_inputs"]},
                {"id": "execute", "name": "execute design points", "expected_outputs": ["observations"]},
                {"id": "validate", "name": "validate outputs", "expected_outputs": ["validation_report"]},
                {"id": "analyze", "name": "analyze response behavior", "expected_outputs": ["summary_metrics"]},
            ],
            analysis_plan={"primary_method": "response_surface_scan", "secondary_methods": ["extrema_detection"]},
            provenance_refs=source_refs[:12],
        )
        return {
            "plugin_id": self.plugin_id,
            "design_matrix": design,
            "experiment_ir": ir.model_dump(),
            "literature_fingerprint": {
                "mean_relevance": fp["mean_relevance"],
                "n_studies": fp["n_studies"],
                "top_tokens": fp.get("top_tokens", []),
            },
            "simulation": sim_cfg,
        }

    def validate_feasibility(self, run: RunRecord, experiment_ir_artifact: dict[str, Any]) -> dict[str, Any]:
        design = list(experiment_ir_artifact.get("design_matrix") or [])
        studies = list(run.pipeline.intake.literature.get("studies") or [])
        fp = literature_fingerprint(studies, run.user_goal)
        return feasibility_from_literature_and_design(run, design, fp)

    def score_value(self, run: RunRecord, experiment_ir_artifact: dict[str, Any]) -> dict[str, Any]:
        design = list(experiment_ir_artifact.get("design_matrix") or [])
        studies = list(run.pipeline.intake.literature.get("studies") or [])
        fp = literature_fingerprint(studies, run.user_goal)
        prior = run.pipeline.intake.prior_work
        measurements = run_measurements(run, design, fp) if design else []
        return value_scores_from_context(fp, measurements, dict(prior))

    def generate_protocol(self, run: RunRecord, experiment_ir_artifact: dict[str, Any]) -> dict[str, Any]:
        design = list(experiment_ir_artifact.get("design_matrix") or [])
        return protocol_from_design(run, design)

    def schedule(self, run: RunRecord, experiment_ir_artifact: dict[str, Any]) -> dict[str, Any]:
        design = list(experiment_ir_artifact.get("design_matrix") or [])
        studies = list(run.pipeline.intake.literature.get("studies") or [])
        fp = literature_fingerprint(studies, run.user_goal)
        return schedule_from_design(run, design, fp)

    def execute(self, run: RunRecord, experiment_ir_artifact: dict[str, Any]) -> dict[str, Any]:
        design = list(experiment_ir_artifact.get("design_matrix") or [])
        studies = list(run.pipeline.intake.literature.get("studies") or [])
        fp = literature_fingerprint(studies, run.user_goal)
        measurements = run_measurements(run, design, fp) if design else []
        payload = execution_payload(run, design, measurements, fp)
        axis_hints = dict((run.pipeline.intake.literature or {}).get("axis_hints") or {})
        series_list = list(payload.get("series_for_charts") or [])
        if series_list and isinstance(series_list[0], dict):
            series = dict(series_list[0])
            series["x_label"] = str(axis_hints.get("x_label") or "Temperature")
            series["x_unit"] = str(axis_hints.get("x_unit") or "C")
            series["y_label"] = str(axis_hints.get("y_label") or "Conductivity")
            series["y_unit"] = str(axis_hints.get("y_unit") or "S/cm")
            series["y_format"] = str(axis_hints.get("y_format") or "scientific")
            series["x_key"] = "temperature_c"
            series["y_key"] = "sigma_S_cm"
            payload["series_for_charts"] = [series]
        payload["plugin_fidelity"] = "medium"
        payload["origin"] = "simulated"
        return payload

    def recover(self, run: RunRecord, execution_log: dict[str, Any]) -> dict[str, Any]:
        measurements = list(execution_log.get("measurements") or [])
        return recovery_payload(measurements)

    def validate_results(self, run: RunRecord, execution_log: dict[str, Any]) -> dict[str, Any]:
        measurements = list(execution_log.get("measurements") or [])
        return validation_payload(measurements)

    def interpret(self, run: RunRecord, execution_log: dict[str, Any]) -> dict[str, Any]:
        measurements = list(execution_log.get("measurements") or [])
        return interpret_from_measurements(measurements)

    def recommend_next(self, run: RunRecord, execution_log: dict[str, Any]) -> dict[str, Any]:
        measurements = list(execution_log.get("measurements") or [])
        studies = list(run.pipeline.intake.literature.get("studies") or [])
        fp = literature_fingerprint(studies, run.user_goal)
        return recommend_next_from_measurements(measurements, fp)

    def report(self, run: RunRecord, execution_log: dict[str, Any], interpretation: dict[str, Any]) -> dict[str, Any]:
        measurements = list(execution_log.get("measurements") or [])
        return report_payload(run, measurements, interpretation)
