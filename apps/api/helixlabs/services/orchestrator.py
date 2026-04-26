from __future__ import annotations

from helixlabs.domain.models import PipelinePayload, ProvenanceEvent, RunRecord, RunState
from helixlabs.repos.json_run_repository import JsonRunRepository
from helixlabs.services.stage_service import StageService


class RunOrchestrator:
    def __init__(self, repo: JsonRunRepository, stage_service: StageService) -> None:
        self._repo = repo
        self._stage_service = stage_service

    def create_run(
        self,
        run_id: str,
        user_goal: str,
        plugin_override: str | None = None,
        simulation_overrides: dict[str, str | int | float] | None = None,
    ) -> RunRecord:
        artifacts: dict[str, object] = {}
        if plugin_override:
            artifacts["plugin_override"] = plugin_override
        if simulation_overrides:
            artifacts["simulation_overrides"] = simulation_overrides
        run = RunRecord(
            run_id=run_id,
            user_goal=user_goal,
            state=RunState.CREATED,
            pipeline=PipelinePayload(),
            artifacts=artifacts,
            provenance=[],
            created_at=RunRecord.now_iso(),
            updated_at=RunRecord.now_iso(),
        )
        self._repo.save(run)
        # Preserve existing UI behavior: intake is materialized immediately on run creation.
        for stage in [
            "parse-goal",
            "search-literature",
            "match-prior-work",
            "check-negative-results",
            "build-claim-graph",
        ]:
            run = self.run_stage(run_id, stage) or run
        return run

    def get_run(self, run_id: str) -> RunRecord | None:
        return self._repo.get(run_id)

    def list_runs(self, limit: int = 100) -> list[RunRecord]:
        return self._repo.list_runs(limit=limit)

    def set_simulation_overrides(self, run_id: str, overrides: dict[str, str | int | float]) -> RunRecord | None:
        run = self._repo.get(run_id)
        if run is None:
            return None
        run.artifacts["simulation_overrides"] = overrides
        run.updated_at = RunRecord.now_iso()
        self._repo.save(run)
        return run

    def replan(self, run_id: str) -> RunRecord | None:
        run = self._repo.get(run_id)
        if run is None:
            return None
        allowed = {
            RunState.CLAIM_GRAPH_BUILT,
            RunState.EXPERIMENT_IR_COMPILED,
            RunState.FEASIBILITY_VALIDATED,
            RunState.NOVELTY_VALUE_SCORED,
            RunState.PROTOCOL_GENERATED,
            RunState.AWAITING_HUMAN_APPROVAL,
        }
        if run.state not in allowed:
            raise ValueError(f"Cannot replan from state '{run.state.value}'")
        run.state = RunState.CLAIM_GRAPH_BUILT
        run.pipeline.planning.compiler = {}
        run.pipeline.planning.schedule = {}
        for key in [
            "experiment_ir",
            "feasibility_report",
            "value_score",
            "protocol",
            "schedule",
            "normalized_results",
            "execution_log",
            "failure_recovery_plan",
            "validation_report",
            "interpretation",
            "next_experiment_recommendation",
            "report",
            "memory_update",
        ]:
            run.artifacts.pop(key, None)
        run.provenance.append(
            ProvenanceEvent(
                time=RunRecord.now_iso(),
                event_type="DECISION",
                category="Planning",
                message="Simulation controls changed; planning artifacts regenerated.",
            )
        )
        run.updated_at = RunRecord.now_iso()
        self._repo.save(run)
        for stage in ["compile-ir", "validate-feasibility", "score-value", "generate-protocol", "schedule"]:
            run = self.run_stage(run_id, stage) or run
        return run

    def run_stage(self, run_id: str, stage_name: str) -> RunRecord | None:
        run = self._repo.get(run_id)
        if run is None:
            return None

        stage_map = {
            "parse-goal": (RunState.CREATED, RunState.GOAL_PARSED, self._apply_parse_goal),
            "search-literature": (RunState.GOAL_PARSED, RunState.LITERATURE_SEARCHED, self._apply_search_literature),
            "match-prior-work": (RunState.LITERATURE_SEARCHED, RunState.PRIOR_WORK_MATCHED, self._apply_match_prior_work),
            "check-negative-results": (
                RunState.PRIOR_WORK_MATCHED,
                RunState.NEGATIVE_RESULTS_CHECKED,
                self._apply_negative_results,
            ),
            "build-claim-graph": (
                RunState.NEGATIVE_RESULTS_CHECKED,
                RunState.CLAIM_GRAPH_BUILT,
                self._apply_claim_graph,
            ),
            "compile-ir": (RunState.CLAIM_GRAPH_BUILT, RunState.EXPERIMENT_IR_COMPILED, self._apply_compile_ir),
            "validate-feasibility": (
                RunState.EXPERIMENT_IR_COMPILED,
                RunState.FEASIBILITY_VALIDATED,
                self._apply_validate_feasibility,
            ),
            "score-value": (RunState.FEASIBILITY_VALIDATED, RunState.NOVELTY_VALUE_SCORED, self._apply_score_value),
            "generate-protocol": (
                RunState.NOVELTY_VALUE_SCORED,
                RunState.PROTOCOL_GENERATED,
                self._apply_generate_protocol,
            ),
            "schedule": (RunState.PROTOCOL_GENERATED, RunState.AWAITING_HUMAN_APPROVAL, self._apply_schedule),
            "execute": (RunState.APPROVED, RunState.EXECUTION_FAILED_OR_COMPLETED, self._apply_execute),
            "recover": (
                RunState.EXECUTION_FAILED_OR_COMPLETED,
                RunState.RECOVERY_APPLIED,
                self._apply_recover,
            ),
            "validate-results": (RunState.RECOVERY_APPLIED, RunState.RESULTS_REPAIRED, self._apply_validate_results),
            "interpret": (RunState.RESULTS_REPAIRED, RunState.INTERPRETED, self._apply_interpret),
            "recommend-next": (
                RunState.INTERPRETED,
                RunState.NEXT_EXPERIMENT_RECOMMENDED,
                self._apply_recommend_next,
            ),
            "update-memory": (
                RunState.NEXT_EXPERIMENT_RECOMMENDED,
                RunState.MEMORY_UPDATED,
                self._apply_update_memory,
            ),
        }

        if stage_name not in stage_map:
            raise ValueError(f"Unknown stage: {stage_name}")

        required_state, new_state, handler = stage_map[stage_name]
        if run.state != required_state:
            raise ValueError(f"Invalid transition for stage '{stage_name}' from state '{run.state.value}'")

        handler(run)
        run.state = new_state

        run.updated_at = RunRecord.now_iso()
        self._repo.save(run)
        return run

    def approve(self, run_id: str, approved: bool, approved_by: str, notes: str) -> RunRecord | None:
        run = self._repo.get(run_id)
        if run is None:
            return None
        if run.state != RunState.AWAITING_HUMAN_APPROVAL:
            return run
        run.provenance.append(
            ProvenanceEvent(
                time=RunRecord.now_iso(),
                event_type="DECISION",
                category="Approval",
                message=f"Approval={approved} by {approved_by}. Notes: {notes}",
            )
        )
        if approved:
            run.state = RunState.APPROVED
        run.updated_at = RunRecord.now_iso()
        self._repo.save(run)
        return run

    def advance(self, run_id: str) -> RunRecord | None:
        run = self._repo.get(run_id)
        if run is None:
            return None
        auto_sequence = {
            RunState.CREATED: "parse-goal",
            RunState.GOAL_PARSED: "search-literature",
            RunState.LITERATURE_SEARCHED: "match-prior-work",
            RunState.PRIOR_WORK_MATCHED: "check-negative-results",
            RunState.NEGATIVE_RESULTS_CHECKED: "build-claim-graph",
            RunState.CLAIM_GRAPH_BUILT: "compile-ir",
            RunState.EXPERIMENT_IR_COMPILED: "validate-feasibility",
            RunState.FEASIBILITY_VALIDATED: "score-value",
            RunState.NOVELTY_VALUE_SCORED: "generate-protocol",
            RunState.PROTOCOL_GENERATED: "schedule",
            RunState.APPROVED: "execute",
            RunState.EXECUTION_FAILED_OR_COMPLETED: "recover",
            RunState.RECOVERY_APPLIED: "validate-results",
            RunState.RESULTS_REPAIRED: "interpret",
            RunState.INTERPRETED: "recommend-next",
            RunState.NEXT_EXPERIMENT_RECOMMENDED: "update-memory",
        }
        stage = auto_sequence.get(run.state)
        if stage is None:
            return run
        return self.run_stage(run_id, stage)

    def _apply_parse_goal(self, run: RunRecord) -> None:
        payload, events = self._stage_service.stage_parse_goal(run)
        run.pipeline.intake.parsed_goal = payload
        run.artifacts["scientific_intent"] = payload
        run.provenance.extend(events)

    def _apply_search_literature(self, run: RunRecord) -> None:
        payload, events = self._stage_service.stage_search_literature(run)
        run.pipeline.intake.literature = payload
        run.artifacts["literature"] = payload
        run.provenance.extend(events)

    def _apply_match_prior_work(self, run: RunRecord) -> None:
        payload, events = self._stage_service.stage_match_prior_work(run)
        run.pipeline.intake.prior_work = payload
        run.artifacts["prior_work"] = payload
        run.provenance.extend(events)

    def _apply_negative_results(self, run: RunRecord) -> None:
        payload, events = self._stage_service.stage_check_negative_results(run)
        run.artifacts["negative_results"] = payload
        run.provenance.extend(events)

    def _apply_claim_graph(self, run: RunRecord) -> None:
        payload, events = self._stage_service.stage_build_claim_graph(run)
        run.pipeline.intake.claim_graph = payload
        run.artifacts["claim_graph"] = payload
        run.provenance.extend(events)

    def _apply_compile_ir(self, run: RunRecord) -> None:
        payload, events = self._stage_service.stage_compile_ir(run)
        run.pipeline.planning.compiler = payload
        run.artifacts["experiment_ir"] = payload
        run.provenance.extend(events)

    def _apply_validate_feasibility(self, run: RunRecord) -> None:
        payload, events = self._stage_service.stage_validate_feasibility(run)
        run.artifacts["feasibility_report"] = payload
        run.provenance.extend(events)

    def _apply_score_value(self, run: RunRecord) -> None:
        payload, events = self._stage_service.stage_score_value(run)
        run.artifacts["value_score"] = payload
        run.provenance.extend(events)

    def _apply_generate_protocol(self, run: RunRecord) -> None:
        payload, events = self._stage_service.stage_generate_protocol(run)
        run.artifacts["protocol"] = payload
        run.provenance.extend(events)

    def _apply_schedule(self, run: RunRecord) -> None:
        payload, events = self._stage_service.stage_schedule(run)
        run.pipeline.planning.schedule = payload
        run.artifacts["schedule"] = payload
        run.provenance.extend(events)

    def _apply_execute(self, run: RunRecord) -> None:
        payload, events = self._stage_service.stage_execute(run)
        run.pipeline.runtime.execution = payload
        run.artifacts["execution_log"] = payload
        run.artifacts["normalized_results"] = {
            "observations": list(payload.get("measurements") or []),
            "series": list(payload.get("series_for_charts") or []),
            "events": [{"type": e.event_type, "category": e.category, "message": e.message, "time": e.time} for e in events],
            "qc": [],
            "summary_metrics": {},
            "procedure_trace": self._procedure_trace(run=run, status="executed"),
            "fidelity": payload.get("plugin_fidelity", "unknown"),
            "origin": payload.get("origin", "simulated"),
        }
        run.provenance.extend(events)

    def _apply_recover(self, run: RunRecord) -> None:
        payload, events = self._stage_service.stage_recover(run)
        run.pipeline.runtime.recovery = payload
        run.artifacts["failure_recovery_plan"] = payload
        norm = run.artifacts.get("normalized_results") or {}
        norm["recovery"] = payload
        norm["procedure_trace"] = self._procedure_trace(run=run, status="recovered")
        run.artifacts["normalized_results"] = norm
        run.provenance.extend(events)

    def _apply_validate_results(self, run: RunRecord) -> None:
        payload, events = self._stage_service.stage_validate_results(run)
        run.pipeline.runtime.validation = payload
        run.artifacts["validation_report"] = payload
        norm = run.artifacts.get("normalized_results") or {}
        norm["qc"] = [
            {
                "status": payload.get("validation_status", "unknown"),
                "validated_records": payload.get("validated_records", 0),
                "mapped_columns": payload.get("mapped_columns", {}),
            }
        ]
        norm["procedure_trace"] = self._procedure_trace(run=run, status="validated")
        run.artifacts["normalized_results"] = norm
        run.provenance.extend(events)

    def _apply_interpret(self, run: RunRecord) -> None:
        payload, events = self._stage_service.stage_interpret(run)
        run.pipeline.runtime.results = payload
        run.artifacts["interpretation"] = payload
        norm = run.artifacts.get("normalized_results") or {}
        norm["summary_metrics"] = {
            "best_condition": payload.get("best_condition"),
            "inference": payload.get("inference"),
            "uncertainty": payload.get("uncertainty"),
        }
        norm["procedure_trace"] = self._procedure_trace(run=run, status="interpreted")
        run.artifacts["normalized_results"] = norm
        run.provenance.extend(events)

    def _apply_recommend_next(self, run: RunRecord) -> None:
        payload, events = self._stage_service.stage_recommend_next(run)
        run.pipeline.outcomes.next_experiment = payload
        run.artifacts["next_experiment_recommendation"] = payload
        norm = run.artifacts.get("normalized_results") or {}
        norm["next_experiment"] = payload
        norm["procedure_trace"] = self._procedure_trace(run=run, status="recommended")
        run.artifacts["normalized_results"] = norm
        run.provenance.extend(events)

    def _apply_update_memory(self, run: RunRecord) -> None:
        payload, events = self._stage_service.stage_update_memory(run)
        run.artifacts["memory_update"] = payload
        report, report_events = self._stage_service.stage_generate_report(run)
        run.pipeline.outcomes.report = report
        run.artifacts["report"] = report
        norm = run.artifacts.get("normalized_results") or {}
        norm["report"] = report
        norm["procedure_trace"] = self._procedure_trace(run=run, status="completed")
        run.artifacts["normalized_results"] = norm
        run.provenance.extend(events + report_events)

    @staticmethod
    def _procedure_trace(run: RunRecord, status: str) -> list[dict]:
        protocol = run.artifacts.get("protocol") or {}
        steps = list(protocol.get("steps") or [])
        if not steps:
            return [{"id": "unknown", "name": "protocol unavailable", "status": status}]
        out: list[dict] = []
        for i, s in enumerate(steps):
            out.append({"id": f"step_{i+1}", "name": str(s), "status": status})
        return out
