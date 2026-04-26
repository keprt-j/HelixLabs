from __future__ import annotations

import re

from helixlabs.domain.models import (
    IntakePayload,
    OutcomesPayload,
    PlanningPayload,
    ProvenanceEvent,
    RunRecord,
    RuntimePayload,
)
from helixlabs.services.literature_synthesizer import LiteratureSynthesizerService
from helixlabs.services.plugin_router import PluginRouter
from helixlabs.services.plugins.base import ExperimentPlugin
from helixlabs.services.ir_validator import ExperimentIRValidator


class StageService:
    def __init__(
        self,
        synthesizer: LiteratureSynthesizerService | None = None,
        ir_validator: ExperimentIRValidator | None = None,
        plugin_router: PluginRouter | None = None,
    ) -> None:
        self._synthesizer = synthesizer or LiteratureSynthesizerService()
        self._ir_validator = ir_validator or ExperimentIRValidator()
        self._plugin_router = plugin_router or PluginRouter()

    def build_intake(self, run: RunRecord) -> tuple[IntakePayload, list[ProvenanceEvent]]:
        synthesis = self._synthesizer.synthesize(run.user_goal)
        payload = IntakePayload(
            parsed_goal={
                "objective": run.user_goal,
                "domain": "materials_discovery",
                "entities": ["dopant", "temperature", "conductivity"],
            },
            literature={
                "source": synthesis.get("source", "fallback"),
                "studies": synthesis.get("studies", []),
                "reason": synthesis.get("reason"),
            },
            prior_work={
                "novelty_score": synthesis.get("novelty_score", 7.2),
                "redundancy_score": synthesis.get("redundancy_score", 3.1),
                "known_runs": ["RUN-1247", "RUN-1289", "RUN-1301"],
            },
            claim_graph={
                "main_claim": synthesis.get("main_claim", "Fe doping improves ionic conductivity of LLZO"),
                "weakest_claim": synthesis.get("weakest_claim", "phase stability maintained under doping"),
                "next_target": synthesis.get("next_target", "test phase stability at elevated temperatures"),
            },
        )
        source = str(synthesis.get("source", "fallback"))
        if source == "crossref+openai":
            model_msg = "Literature retrieved from Crossref and synthesized with OpenAI"
        elif source == "crossref":
            model_msg = "Literature retrieved from Crossref with deterministic scoring"
        else:
            model_msg = "Literature synthesized via fallback dataset"
        events = [
            self._event("STATE", "Intake", "Goal parsed into structured intent"),
            self._event("MODEL", "Intake", model_msg),
            self._event("MODEL", "Intake", "Novelty and prior-work overlap scored"),
            self._event("DECISION", "Intake", "Weakest claim selected for planning focus"),
        ]
        return payload, events

    def build_planning(self, run: RunRecord) -> tuple[PlanningPayload, list[ProvenanceEvent]]:
        payload = PlanningPayload(
            compiler={
                "variables": {
                    "dopant_type": "Fe",
                    "dopant_concentration_mol_pct": [0.1, 0.5, 1.0, 3.0, 5.0],
                    "temperature_c": [25, 50, 100, 150, 200, 250, 300],
                },
                "success_metrics": {
                    "primary": "sigma_ionic > 5e-4 S/cm",
                    "secondary": "phase_purity > 95%",
                },
            },
            schedule={
                "total_duration_hours": 28,
                "resource_utilization_pct": 67,
                "idle_time_hours": 9.2,
            },
        )
        events = [
            self._event("STATE", "Planning", "Experiment plan compiled from intent"),
            self._event("STATE", "Planning", "Resource schedule generated"),
        ]
        return payload, events

    def build_runtime(self, run: RunRecord) -> tuple[RuntimePayload, list[ProvenanceEvent]]:
        payload = RuntimePayload(
            execution={
                "current_step": 5,
                "total_steps": 9,
                "status": "running",
            },
            recovery={
                "failure_detected": "XRD peak intensity below threshold",
                "selected_recovery": "retry_step_with_repolishing",
            },
            validation={
                "mapped_columns": {
                    "temp_celsius": "temperature",
                    "sigma_ionic": "conductivity",
                    "e_hull": "activation_energy",
                },
                "validated_records": 35,
            },
            results={
                "conductivity_at_25c": 3.8e-4,
                "activation_energy_ev": 0.32,
                "phase_purity_pct": 97.2,
            },
        )
        events = [
            self._event("STATE", "Runtime", "Execution reached measurement phase"),
            self._event("ERROR", "Runtime", "XRD failure detected and classified"),
            self._event("FIX", "Runtime", "Recovery action applied"),
            self._event("FIX", "Runtime", "Schema drift mapped and validated"),
        ]
        return payload, events

    def build_outcomes(self, run: RunRecord) -> tuple[OutcomesPayload, list[ProvenanceEvent]]:
        payload = OutcomesPayload(
            next_experiment={
                "recommendation": "Fine-grained Fe concentration sweep (3.0-7.0 mol%)",
                "expected_info_gain": 8.4,
                "risk_level": 3.2,
            },
            report={
                "summary": "Run completed with improved conductivity and acceptable phase purity.",
                "status": "completed",
            },
        )
        events = [
            self._event("DECISION", "Outcomes", "Next experiment recommendation generated"),
            self._event("STATE", "Outcomes", "Run report finalized"),
        ]
        return payload, events

    def stage_parse_goal(self, run: RunRecord) -> tuple[dict, list[ProvenanceEvent]]:
        g = run.user_goal.lower()
        tokens = [t for t in re.findall(r"[a-zA-Z0-9]{4,}", g) if t not in {"with", "from", "that", "this", "using"}]
        top_entities = list(dict.fromkeys(tokens[:8])) or ["input_factor", "response_metric"]
        if any(k in g for k in ("electrolyte", "conductivity", "dop", "phase", "battery", "chem")):
            domain = "chemistry_materials"
        elif any(k in g for k in ("ad", "ctr", "conversion", "ranking", "pricing", "funnel")):
            domain = "digital_optimization"
        else:
            domain = "generic_experimentation"
        payload = {
            "domain": domain,
            "objective": run.user_goal,
            "entities": top_entities,
        }
        return payload, [self._event("STATE", "Intake", "Goal parsed into structured intent")]

    def stage_search_literature(self, run: RunRecord) -> tuple[dict, list[ProvenanceEvent]]:
        synthesis = self._synthesizer.synthesize(run.user_goal)
        payload = {
            "source": synthesis.get("source", "fallback"),
            "studies": synthesis.get("studies", []),
            "reason": synthesis.get("reason"),
            "axis_hints": synthesis.get("axis_hints", {}),
            "main_claim": synthesis.get("main_claim"),
            "weakest_claim": synthesis.get("weakest_claim"),
            "next_target": synthesis.get("next_target"),
            "novelty_score_hint": synthesis.get("novelty_score"),
            "redundancy_score_hint": synthesis.get("redundancy_score"),
        }
        source = str(payload["source"])
        if source == "crossref+openai":
            msg = "Literature retrieved from Crossref and synthesized with OpenAI"
        elif source == "crossref":
            msg = "Literature retrieved from Crossref with deterministic scoring"
        else:
            msg = "Literature synthesized via fallback dataset"
        return payload, [self._event("MODEL", "Intake", msg)]

    def stage_match_prior_work(self, run: RunRecord) -> tuple[dict, list[ProvenanceEvent]]:
        studies = run.pipeline.intake.literature.get("studies", [])
        lit = run.pipeline.intake.literature
        novelty = float(lit.get("novelty_score_hint") or 7.2)
        redundancy = float(lit.get("redundancy_score_hint") or 3.1)
        if studies and (lit.get("novelty_score_hint") is None):
            rel = [float(s.get("relevance", 0.0)) for s in studies]
            avg_rel = sum(rel) / max(1, len(rel))
            novelty = max(0.0, min(10.0, round((1.0 - avg_rel) * 8.0 + 2.0, 1)))
            redundancy = max(0.0, min(10.0, round(avg_rel * 8.0 + 1.0, 1)))
        known_runs: list[str] = []
        for s in sorted(studies, key=lambda x: float(x.get("relevance", 0.0)), reverse=True)[:5]:
            doi = str(s.get("doi", "")).strip()
            title = str(s.get("title", ""))[:72]
            if doi:
                known_runs.append(f"{doi} — {title}")
            elif title:
                known_runs.append(title)
        if not known_runs:
            known_runs = ["No DOI-tagged studies in bundle; broaden query or check retrieval."]
        top = studies[0] if studies else {}
        gap = (
            f"Corpus emphasizes {str(top.get('title', 'retrieved work'))[:90]}…; "
            "intermediate operating points may still be under-sampled for your stated goal."
            if studies
            else "Limited literature bundle; empirical coverage of your goal is uncertain."
        )
        payload = {
            "novelty_score": novelty,
            "redundancy_score": redundancy,
            "known_runs": known_runs,
            "gap": gap,
        }
        return payload, [self._event("MODEL", "Intake", "Novelty and prior-work overlap scored")]

    def stage_check_negative_results(self, run: RunRecord) -> tuple[dict, list[ProvenanceEvent]]:
        studies = list(run.pipeline.intake.literature.get("studies") or [])
        neg: list[dict[str, str]] = []
        for s in studies:
            rel = float(s.get("relevance", 1.0))
            if rel >= 0.35:
                continue
            lim = str(s.get("limitations", s.get("findings", "")))[:200]
            neg.append(
                {
                    "condition": f"Low-evidence match (relevance={rel:.2f}): {str(s.get('title',''))[:80]}",
                    "failure_type": "weak_literature_anchor",
                    "recommendation": lim or "Treat as weak prior; prioritize direct measurements.",
                }
            )
        for s in studies:
            blob = f"{s.get('title','')} {s.get('abstract','')} {s.get('findings','')}".lower()
            if any(k in blob for k in ("decompos", "instab", "failed", "crack", "short-circuit")):
                neg.append(
                    {
                        "condition": str(s.get("title", "Study"))[:100],
                        "failure_type": "reported_adverse_outcome",
                        "recommendation": "Carry forward as risk signal in planning and simulation stress paths.",
                    }
                )
                break
        if not neg:
            neg.append(
                {
                    "condition": "upper exploration bound",
                    "failure_type": "hypothetical_stability_stress",
                    "recommendation": "Reserve capacity for boundary sweeps informed by simulation phase_proxy.",
                }
            )
        payload = {"negative_results": neg[:6]}
        return payload, [self._event("STATE", "Intake", "Negative-results memory checked")]

    def stage_build_claim_graph(self, run: RunRecord) -> tuple[dict, list[ProvenanceEvent]]:
        prior = run.pipeline.intake.prior_work
        lit = run.pipeline.intake.literature
        main_claim = str(
            lit.get("main_claim") or "Targeted composition changes can move the target property in a favorable direction."
        )
        weakest_claim = str(
            lit.get("weakest_claim") or "Reported gains persist under the full operating envelope you care about."
        )
        next_target = str(
            lit.get("next_target") or "Stress boundary conditions implied by the weakest evidence in the bundle."
        )
        payload = {
            "main_claim": main_claim,
            "weakest_claim": weakest_claim,
            "next_target": next_target,
            "context": {
                "novelty_score": prior.get("novelty_score", 7.2),
                "redundancy_score": prior.get("redundancy_score", 3.1),
                "source_dois": [str(s.get("doi", "")) for s in list(lit.get("studies") or []) if s.get("doi")][:5],
            },
        }
        return payload, [self._event("DECISION", "Intake", "Weakest claim selected for planning focus")]

    def stage_compile_ir(self, run: RunRecord) -> tuple[dict, list[ProvenanceEvent]]:
        plugin = self._plugin_for_run(run)
        selected = self._plugin_router.select(run)
        confidence = selected.confidence if selected.plugin.plugin_id == plugin.plugin_id else 1.0
        reason = selected.reason if selected.plugin.plugin_id == plugin.plugin_id else f"Plugin override selected '{plugin.plugin_id}'"
        plugin_payload = plugin.compile_ir(run)
        validation = self._ir_validator.validate(plugin_payload.get("experiment_ir") or {})
        payload = {
            "experiment_type": f"plugin:{selected.plugin.plugin_id}",
            "variables": list((validation.get("normalized_ir") or {}).get("factors") or []),
            "design_matrix": plugin_payload.get("design_matrix", []),
            "target_claim": run.pipeline.intake.claim_graph.get("weakest_claim"),
            "simulation": plugin_payload.get("simulation", {}),
            "experiment_ir": validation.get("normalized_ir") or plugin_payload.get("experiment_ir") or {},
            "ir_validation": {
                "is_valid": validation["is_valid"],
                "errors": validation["errors"],
                "warnings": validation["warnings"],
            },
            "literature_fingerprint": plugin_payload.get("literature_fingerprint", {}),
            "plugin": {
                "selected_plugin": plugin.plugin_id,
                "selection_confidence": round(confidence, 4),
                "selection_reason": reason,
            },
        }
        msg = "Experiment IR compiled from literature-conditioned design grid"
        if not validation["is_valid"]:
            msg += " (with validation errors)"
        return payload, [self._event("STATE", "Planning", msg)]

    def stage_validate_feasibility(self, run: RunRecord) -> tuple[dict, list[ProvenanceEvent]]:
        ir = run.artifacts.get("experiment_ir") or {}
        payload = self._plugin_for_run(run).validate_feasibility(run, ir)
        return payload, [self._event("STATE", "Planning", "Feasibility validated by selected execution plugin")]

    def stage_score_value(self, run: RunRecord) -> tuple[dict, list[ProvenanceEvent]]:
        ir = run.artifacts.get("experiment_ir") or {}
        payload = self._plugin_for_run(run).score_value(run, ir)
        return payload, [self._event("STATE", "Planning", "Experiment value scored by selected execution plugin")]

    def stage_generate_protocol(self, run: RunRecord) -> tuple[dict, list[ProvenanceEvent]]:
        ir = run.artifacts.get("experiment_ir") or {}
        payload = self._plugin_for_run(run).generate_protocol(run, ir)
        return payload, [self._event("STATE", "Planning", "Protocol generated by selected execution plugin")]

    def stage_schedule(self, run: RunRecord) -> tuple[dict, list[ProvenanceEvent]]:
        ir = run.artifacts.get("experiment_ir") or {}
        payload = self._plugin_for_run(run).schedule(run, ir)
        return payload, [self._event("STATE", "Planning", "Resource schedule generated by selected execution plugin")]

    def stage_execute(self, run: RunRecord) -> tuple[dict, list[ProvenanceEvent]]:
        ir = run.artifacts.get("experiment_ir") or {}
        payload = self._plugin_for_run(run).execute(run, ir)
        events = [
            self._event("STATE", "Runtime", "Execution plugin campaign executed"),
        ]
        if payload.get("recovery_hint"):
            events.append(self._event("ERROR", "Runtime", "Execution plugin flagged recovery condition"))
        return payload, events

    def stage_recover(self, run: RunRecord) -> tuple[dict, list[ProvenanceEvent]]:
        ex = run.artifacts.get("execution_log") or {}
        payload = self._plugin_for_run(run).recover(run, ex)
        return payload, [self._event("FIX", "Runtime", "Recovery policy applied from execution plugin")]

    def stage_validate_results(self, run: RunRecord) -> tuple[dict, list[ProvenanceEvent]]:
        ex = run.artifacts.get("execution_log") or {}
        payload = self._plugin_for_run(run).validate_results(run, ex)
        return payload, [self._event("FIX", "Runtime", "Measurement bundle validated")]

    def stage_interpret(self, run: RunRecord) -> tuple[dict, list[ProvenanceEvent]]:
        ex = run.artifacts.get("execution_log") or {}
        payload = self._plugin_for_run(run).interpret(run, ex)
        return payload, [self._event("STATE", "Runtime", "Results interpreted from execution plugin outputs")]

    def stage_recommend_next(self, run: RunRecord) -> tuple[dict, list[ProvenanceEvent]]:
        ex = run.artifacts.get("execution_log") or {}
        payload = self._plugin_for_run(run).recommend_next(run, ex)
        return payload, [self._event("DECISION", "Outcomes", "Next experiment recommendation generated by execution plugin")]

    def stage_update_memory(self, run: RunRecord) -> tuple[dict, list[ProvenanceEvent]]:
        payload = {
            "memory_updated": True,
            "updated_records": [run.run_id],
        }
        return payload, [self._event("STATE", "Outcomes", "Experiment memory updated")]

    def stage_generate_report(self, run: RunRecord) -> tuple[dict, list[ProvenanceEvent]]:
        ex = run.artifacts.get("execution_log") or {}
        measurements = list(ex.get("measurements") or [])
        interp = run.artifacts.get("interpretation") or {}
        payload = self._plugin_for_run(run).report(run, ex, dict(interp))
        payload["n_measurements"] = payload.get("n_measurements", len(measurements))
        return payload, [self._event("STATE", "Outcomes", "Run report finalized with plugin execution trace")]

    @staticmethod
    def _event(event_type: str, category: str, message: str) -> ProvenanceEvent:
        return ProvenanceEvent(
            time=RunRecord.now_iso(),
            event_type=event_type,
            category=category,
            message=message,
        )

    def _plugin_for_run(self, run: RunRecord) -> ExperimentPlugin:
        override = run.artifacts.get("plugin_override")
        if isinstance(override, str) and override.strip():
            plugin = self._plugin_router.by_id(override.strip())
            if plugin is not None:
                return plugin
        plugin_meta = (run.artifacts.get("experiment_ir") or {}).get("plugin") or {}
        plugin_id = plugin_meta.get("selected_plugin")
        if isinstance(plugin_id, str):
            plugin = self._plugin_router.by_id(plugin_id)
            if plugin is not None:
                return plugin
        return self._plugin_router.select(run).plugin
