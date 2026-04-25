from __future__ import annotations

from pathlib import Path
from typing import Any

from packages.agents.claim_graph_builder import build_claim_graph
from packages.agents.intent_parser import parse_scientific_intent
from packages.agents.next_experiment_planner import plan_next_experiment
from packages.agents.result_interpreter import interpret_results
from packages.compiler.compiler import compile_experiment_ir
from packages.compiler.feasibility_validator import validate_feasibility
from packages.compiler.protocol_generator import generate_protocol
from packages.compiler.value_scorer import score_experiment_value
from packages.execution.adapters.simulated_lab import execute_simulated_lab
from packages.execution.recovery import build_recovery_plan
from packages.literature.evidence_extractor import extract_evidence
from packages.literature.experiment_matcher import match_prior_work
from packages.literature.search import search_literature
from packages.models import (
    ApprovalEvent,
    ExperimentIR,
    ExperimentRun,
    ExecutionLog,
    Protocol,
    RepairedResult,
    RunState,
)
from packages.prior_work.negative_results import find_negative_results
from packages.provenance.event_log import record_event
from packages.provenance.report_generator import generate_report
from packages.scheduler.scheduler import schedule_protocol
from packages.storage import JsonStore, load_json
from packages.validation.data_stent import validate_and_repair


CANONICAL_GOAL = "Find a low-cost cobalt-free cathode material and test whether Mn doping improves conductivity without hurting stability."


class WorkflowError(ValueError):
    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None) -> None:
        self.code = code
        self.details = details or {}
        super().__init__(message)


class HelixWorkflow:
    def __init__(self, root: Path, store: JsonStore) -> None:
        self.root = root
        self.store = store

    def create_run(self, user_goal: str) -> ExperimentRun:
        run = self.store.create_run(user_goal=user_goal or CANONICAL_GOAL)
        record_event(
            self.store,
            run.id,
            "run_created",
            "Created HelixLabs experiment run.",
            "api",
            {"user_goal": run.user_goal},
        )
        return run

    def get_payload(self, run_id: str) -> dict[str, Any]:
        run = self.store.get_run(run_id)
        return {
            "run": run.model_dump(mode="json"),
            "artifacts": run.artifacts,
            "provenance_events": [event.model_dump(mode="json") for event in self.store.get_events(run_id)],
        }

    def parse_goal(self, run_id: str) -> dict[str, Any]:
        run = self.store.get_run(run_id)
        intent = parse_scientific_intent(run.user_goal)
        run.artifacts["scientific_intent"] = intent.model_dump(mode="json")
        self._set_state(run, RunState.GOAL_PARSED)
        self.store.save_run(run)
        record_event(self.store, run.id, "goal_parsed", "Parsed scientific intent into structured constraints.", "intent_parser", run.artifacts["scientific_intent"])
        return {"scientific_intent": run.artifacts["scientific_intent"]}

    def search_literature(self, run_id: str, force_fallback: bool = False) -> dict[str, Any]:
        run = self.store.get_run(run_id)
        self._require(run, RunState.GOAL_PARSED)
        query_plan, papers, retrieval_mode = search_literature(self.root, force_fallback=force_fallback)
        run.artifacts["query_plan"] = query_plan.model_dump(mode="json")
        run.artifacts["retrieved_papers"] = [paper.model_dump(mode="json") for paper in papers]
        run.artifacts["retrieval_mode"] = retrieval_mode
        self._set_state(run, RunState.LITERATURE_SEARCHED)
        self.store.save_run(run)
        record_event(self.store, run.id, "literature_searched", f"Retrieved {len(papers)} papers using {retrieval_mode}.", "literature_search", {"queries": run.artifacts["query_plan"], "retrieval_mode": retrieval_mode})
        return {"query_plan": run.artifacts["query_plan"], "retrieved_papers": run.artifacts["retrieved_papers"], "retrieval_mode": retrieval_mode}

    def match_prior_work(self, run_id: str) -> dict[str, Any]:
        run = self.store.get_run(run_id)
        self._require(run, RunState.LITERATURE_SEARCHED)
        from packages.models import RetrievedPaper

        papers = [RetrievedPaper.model_validate(item) for item in run.artifacts.get("retrieved_papers", [])]
        evidence = extract_evidence(papers)
        prior_match = match_prior_work(self.root)
        run.artifacts["evidence_extractions"] = [item.model_dump(mode="json") for item in evidence]
        run.artifacts["prior_work_match"] = prior_match.model_dump(mode="json")
        self._set_state(run, RunState.PRIOR_WORK_MATCHED)
        self.store.save_run(run)
        record_event(self.store, run.id, "prior_work_matched", "Identified low-Mn prior tests and unresolved 10-20% gap.", "experiment_matcher", run.artifacts["prior_work_match"])
        return {"evidence_extractions": run.artifacts["evidence_extractions"], "prior_work_match": run.artifacts["prior_work_match"]}

    def check_negative_results(self, run_id: str) -> dict[str, Any]:
        run = self.store.get_run(run_id)
        self._require(run, RunState.PRIOR_WORK_MATCHED)
        negative_results = find_negative_results(self.root)
        run.artifacts["negative_results"] = [item.model_dump(mode="json") for item in negative_results]
        self._set_state(run, RunState.NEGATIVE_RESULTS_CHECKED)
        self.store.save_run(run)
        record_event(self.store, run.id, "negative_results_checked", "Found prior 20% Mn stability failure.", "negative_results_memory", {"negative_results": run.artifacts["negative_results"]})
        return {"negative_results": run.artifacts["negative_results"]}

    def build_claim_graph(self, run_id: str) -> dict[str, Any]:
        run = self.store.get_run(run_id)
        self._require(run, RunState.NEGATIVE_RESULTS_CHECKED)
        graph = build_claim_graph()
        run.artifacts["claim_graph"] = graph.model_dump(mode="json")
        self._set_state(run, RunState.CLAIM_GRAPH_BUILT)
        self.store.save_run(run)
        record_event(self.store, run.id, "claim_graph_built", "Built claim graph and selected C3 as weakest high-value claim.", "claim_graph_builder", run.artifacts["claim_graph"])
        return {"claim_graph": run.artifacts["claim_graph"]}

    def compile_ir(self, run_id: str) -> dict[str, Any]:
        run = self.store.get_run(run_id)
        self._require(run, RunState.CLAIM_GRAPH_BUILT)
        ir = compile_experiment_ir()
        run.artifacts["experiment_ir"] = ir.model_dump(mode="json")
        self._set_state(run, RunState.EXPERIMENT_IR_COMPILED)
        self.store.save_run(run)
        record_event(self.store, run.id, "experiment_ir_compiled", "Compiled 12%, 14%, and 16% Mn boundary screen.", "experiment_ir_compiler", run.artifacts["experiment_ir"])
        return {"experiment_ir": run.artifacts["experiment_ir"]}

    def validate_feasibility(self, run_id: str) -> dict[str, Any]:
        run = self.store.get_run(run_id)
        self._require(run, RunState.EXPERIMENT_IR_COMPILED)
        ir = ExperimentIR.model_validate(run.artifacts["experiment_ir"])
        report = validate_feasibility(self.root, ir)
        run.artifacts["feasibility_report"] = report.model_dump(mode="json")
        self._set_state(run, RunState.FEASIBILITY_VALIDATED)
        self.store.save_run(run)
        record_event(self.store, run.id, "feasibility_validated", "Validated controls, resources, schema, redundancy, and risk warnings.", "feasibility_validator", run.artifacts["feasibility_report"])
        return {"feasibility_report": run.artifacts["feasibility_report"]}

    def score_value(self, run_id: str) -> dict[str, Any]:
        run = self.store.get_run(run_id)
        self._require(run, RunState.FEASIBILITY_VALIDATED)
        score = score_experiment_value()
        run.artifacts["value_score"] = score.model_dump(mode="json")
        self._set_state(run, RunState.NOVELTY_VALUE_SCORED)
        self.store.save_run(run)
        record_event(self.store, run.id, "novelty_value_scored", "Scored narrowed experiment as high-value and low-redundancy.", "value_scorer", run.artifacts["value_score"])
        return {"value_score": run.artifacts["value_score"]}

    def generate_protocol(self, run_id: str) -> dict[str, Any]:
        run = self.store.get_run(run_id)
        self._require(run, RunState.NOVELTY_VALUE_SCORED)
        protocol = generate_protocol()
        run.artifacts["protocol"] = protocol.model_dump(mode="json")
        self._set_state(run, RunState.PROTOCOL_GENERATED)
        self.store.save_run(run)
        record_event(self.store, run.id, "protocol_generated", "Generated structured cloud-lab protocol.", "protocol_generator", run.artifacts["protocol"])
        return {"protocol": run.artifacts["protocol"]}

    def schedule(self, run_id: str) -> dict[str, Any]:
        run = self.store.get_run(run_id)
        self._require(run, RunState.PROTOCOL_GENERATED)
        protocol = Protocol.model_validate(run.artifacts["protocol"])
        schedule = schedule_protocol(self.root, protocol)
        run.artifacts["schedule"] = schedule.model_dump(mode="json")
        self._set_state(run, RunState.SCHEDULED)
        self.store.save_run(run)
        record_event(self.store, run.id, "scheduled", "Scheduled protocol across simulated lab resources.", "scheduler", run.artifacts["schedule"])
        return {"schedule": run.artifacts["schedule"]}

    def await_approval(self, run_id: str) -> dict[str, Any]:
        run = self.store.get_run(run_id)
        self._require(run, RunState.SCHEDULED)
        run.artifacts["approval_gate"] = {
            "summary": "Human approval required before execution.",
            "shows": ["hypothesis", "prior_work", "warnings", "schedule", "expected_output_schema", "recovery_policy"],
        }
        self._set_state(run, RunState.AWAITING_HUMAN_APPROVAL)
        self.store.save_run(run)
        record_event(self.store, run.id, "awaiting_human_approval", "Paused for human approval before execution.", "governance_gate", run.artifacts["approval_gate"])
        return {"approval_gate": run.artifacts["approval_gate"], "state": run.state.value}

    def approve(self, run_id: str, approved: bool, approved_by: str, notes: str) -> dict[str, Any]:
        run = self.store.get_run(run_id)
        self._require(run, RunState.AWAITING_HUMAN_APPROVAL)
        event = ApprovalEvent(
            approval_id="APP-001",
            run_id=run.id,
            approved=approved,
            approved_by=approved_by,
            notes=notes,
        )
        run.artifacts["approval_event"] = event.model_dump(mode="json")
        if approved:
            self._set_state(run, RunState.APPROVED)
        self.store.save_run(run)
        record_event(self.store, run.id, "approved" if approved else "approval_rejected", "Recorded human approval decision.", "demo_user", run.artifacts["approval_event"])
        return {"approval_event": run.artifacts["approval_event"], "state": run.state.value}

    def execute(self, run_id: str) -> dict[str, Any]:
        run = self.store.get_run(run_id)
        self._require(run, RunState.APPROVED)
        self._set_state(run, RunState.EXECUTING)
        record_event(self.store, run.id, "executing", "Execution started on simulated lab adapter.", "simulated_lab", {})
        log = execute_simulated_lab()
        run.artifacts["execution_log"] = log.model_dump(mode="json")
        self._set_state(run, RunState.EXECUTION_FAILED_OR_COMPLETED)
        self.store.save_run(run)
        record_event(self.store, run.id, "execution_failed_or_completed", "Execution produced drifted output after a simulated timeout.", "simulated_lab", run.artifacts["execution_log"])
        return {"execution_log": run.artifacts["execution_log"], "state": run.state.value}

    def recover(self, run_id: str) -> dict[str, Any]:
        run = self.store.get_run(run_id)
        self._require(run, RunState.EXECUTION_FAILED_OR_COMPLETED)
        plan = build_recovery_plan()
        run.artifacts["failure_recovery_plan"] = plan.model_dump(mode="json")
        self._set_state(run, RunState.RECOVERY_APPLIED)
        self.store.save_run(run)
        record_event(self.store, run.id, "recovery_applied", "Selected retry_failed_condition rather than rerun_full_experiment.", "failure_recovery_engine", run.artifacts["failure_recovery_plan"])
        return {"failure_recovery_plan": run.artifacts["failure_recovery_plan"], "state": run.state.value}

    def collect_results(self, run_id: str) -> dict[str, Any]:
        run = self.store.get_run(run_id)
        self._require(run, RunState.RECOVERY_APPLIED)
        execution = ExecutionLog.model_validate(run.artifacts["execution_log"])
        run.artifacts["result_file"] = {
            "format": "csv",
            "schema_status": "drifted",
            "raw_result_csv": execution.raw_result_csv,
        }
        self._set_state(run, RunState.RESULTS_COLLECTED)
        self.store.save_run(run)
        record_event(self.store, run.id, "results_collected", "Collected raw CSV results with intentional schema drift.", "simulated_lab", run.artifacts["result_file"])
        return {"result_file": run.artifacts["result_file"], "state": run.state.value}

    def validate_results(self, run_id: str) -> dict[str, Any]:
        run = self.store.get_run(run_id)
        if run.state == RunState.RECOVERY_APPLIED:
            self.collect_results(run_id)
            run = self.store.get_run(run_id)
        self._require(run, RunState.RESULTS_COLLECTED)
        raw_csv = run.artifacts["result_file"]["raw_result_csv"]
        validation_report, repaired = validate_and_repair(raw_csv)
        run.artifacts["validation_report"] = validation_report.model_dump(mode="json")
        self._set_state(run, RunState.RESULTS_VALIDATED)
        record_event(self.store, run.id, "results_validated", "Detected column drift in raw result CSV.", "data_stent", run.artifacts["validation_report"])
        run.artifacts["repaired_results"] = [item.model_dump(mode="json") for item in repaired]
        self._set_state(run, RunState.RESULTS_REPAIRED)
        self.store.save_run(run)
        record_event(self.store, run.id, "schema_repair", "Mapped drifted columns to materials_screen_v1.", "data_stent", {"repaired_results": run.artifacts["repaired_results"]})
        return {"validation_report": run.artifacts["validation_report"], "repaired_results": run.artifacts["repaired_results"], "state": run.state.value}

    def interpret(self, run_id: str) -> dict[str, Any]:
        run = self.store.get_run(run_id)
        self._require(run, RunState.RESULTS_REPAIRED)
        repaired = [RepairedResult.model_validate(item) for item in run.artifacts["repaired_results"]]
        interpretation = interpret_results(repaired)
        run.artifacts["interpretation"] = interpretation.model_dump(mode="json")
        self._set_state(run, RunState.INTERPRETED)
        self.store.save_run(run)
        record_event(self.store, run.id, "interpreted", "Separated observations, prior evidence, inference, uncertainty, and limitations.", "result_interpreter", run.artifacts["interpretation"])
        return {"interpretation": run.artifacts["interpretation"]}

    def recommend_next(self, run_id: str) -> dict[str, Any]:
        run = self.store.get_run(run_id)
        self._require(run, RunState.INTERPRETED)
        recommendation = plan_next_experiment()
        run.artifacts["next_experiment_recommendation"] = recommendation.model_dump(mode="json")
        self._set_state(run, RunState.NEXT_EXPERIMENT_RECOMMENDED)
        self.store.save_run(run)
        record_event(self.store, run.id, "next_experiment_recommended", "Recommended 14.5%, 15.0%, and 15.5% Mn boundary screen.", "next_experiment_planner", run.artifacts["next_experiment_recommendation"])
        return {"next_experiment_recommendation": run.artifacts["next_experiment_recommendation"]}

    def get_report(self, run_id: str) -> dict[str, Any]:
        run = self.store.get_run(run_id)
        if run.state == RunState.NEXT_EXPERIMENT_RECOMMENDED:
            report = generate_report(run, self.store.get_events(run.id))
            run.artifacts["report"] = report.model_dump(mode="json")
            self._set_state(run, RunState.REPORT_GENERATED)
            self.store.save_run(run)
            record_event(self.store, run.id, "report_generated", "Generated provenance report covering every major stage.", "report_generator", {"section_count": len(report.sections)})
            run = self.store.get_run(run_id)
        elif "report" not in run.artifacts:
            report = generate_report(run, self.store.get_events(run.id))
            run.artifacts["report"] = report.model_dump(mode="json")
            self.store.save_run(run)
        return {"report": run.artifacts["report"]}

    def update_memory(self, run_id: str) -> dict[str, Any]:
        run = self.store.get_run(run_id)
        if run.state == RunState.NEXT_EXPERIMENT_RECOMMENDED:
            self.get_report(run_id)
            run = self.store.get_run(run_id)
        self._require(run, RunState.REPORT_GENERATED)
        memory = load_json(self.root, "data/experiment_memory.json")
        record = {
            "run_id": run.id,
            "experiment": "LiFePO4 Mn boundary screen",
            "tested_values": [0.12, 0.14, 0.16],
            "result": "12% and 14% stable; 16% failed stability.",
            "next_experiment": "14.5%, 15.0%, 15.5% Mn boundary screen",
        }
        if not any(item.get("run_id") == run.id for item in memory):
            memory.append(record)
            (self.root / "data" / "experiment_memory.json").write_text(__import__("json").dumps(memory, indent=2), encoding="utf-8")
        run.artifacts["memory_update"] = {"memory_updated": True, "updated_records": [record]}
        self._set_state(run, RunState.MEMORY_UPDATED)
        self.store.save_run(run)
        record_event(self.store, run.id, "memory_updated", "Updated experiment memory with completed boundary screen.", "experiment_memory", run.artifacts["memory_update"])
        return run.artifacts["memory_update"]

    def advance(self, run_id: str) -> dict[str, Any]:
        run = self.store.get_run(run_id)
        previous = run.state
        action_by_state = {
            RunState.CREATED: lambda: self.parse_goal(run_id),
            RunState.GOAL_PARSED: lambda: self.search_literature(run_id),
            RunState.LITERATURE_SEARCHED: lambda: self.match_prior_work(run_id),
            RunState.PRIOR_WORK_MATCHED: lambda: self.check_negative_results(run_id),
            RunState.NEGATIVE_RESULTS_CHECKED: lambda: self.build_claim_graph(run_id),
            RunState.CLAIM_GRAPH_BUILT: lambda: self.compile_ir(run_id),
            RunState.EXPERIMENT_IR_COMPILED: lambda: self.validate_feasibility(run_id),
            RunState.FEASIBILITY_VALIDATED: lambda: self.score_value(run_id),
            RunState.NOVELTY_VALUE_SCORED: lambda: self.generate_protocol(run_id),
            RunState.PROTOCOL_GENERATED: lambda: self.schedule(run_id),
            RunState.SCHEDULED: lambda: self.await_approval(run_id),
            RunState.APPROVED: lambda: self.execute(run_id),
            RunState.EXECUTION_FAILED_OR_COMPLETED: lambda: self.recover(run_id),
            RunState.RECOVERY_APPLIED: lambda: self.collect_results(run_id),
            RunState.RESULTS_COLLECTED: lambda: self.validate_results(run_id),
            RunState.RESULTS_REPAIRED: lambda: self.interpret(run_id),
            RunState.INTERPRETED: lambda: self.recommend_next(run_id),
            RunState.NEXT_EXPERIMENT_RECOMMENDED: lambda: self.get_report(run_id),
            RunState.REPORT_GENERATED: lambda: self.update_memory(run_id),
        }
        if previous == RunState.AWAITING_HUMAN_APPROVAL:
            raise WorkflowError("APPROVAL_REQUIRED", "Run must be approved before execution.", {"current_state": previous.value, "required_action": "POST /api/runs/{run_id}/approve"})
        if previous not in action_by_state:
            raise WorkflowError("NO_ADVANCE_AVAILABLE", "Run has no further automatic transition.", {"current_state": previous.value})
        result = action_by_state[previous]()
        updated = self.store.get_run(run_id)
        artifact_created = next((key for key in result.keys() if key not in {"state"}), None)
        return {
            "run_id": run_id,
            "previous_state": previous.value,
            "new_state": updated.state.value,
            "artifact_created": artifact_created,
            **result,
        }

    def _set_state(self, run: ExperimentRun, state: RunState) -> None:
        run.state = state

    def _require(self, run: ExperimentRun, state: RunState) -> None:
        if run.state != state:
            raise WorkflowError(
                "INVALID_STATE_TRANSITION",
                f"Run must be in {state.value} before this operation.",
                {"current_state": run.state.value, "required_state": state.value},
            )

