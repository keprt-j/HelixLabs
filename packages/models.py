from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RunState(str, Enum):
    CREATED = "CREATED"
    GOAL_PARSED = "GOAL_PARSED"
    LITERATURE_SEARCHED = "LITERATURE_SEARCHED"
    PRIOR_WORK_MATCHED = "PRIOR_WORK_MATCHED"
    NEGATIVE_RESULTS_CHECKED = "NEGATIVE_RESULTS_CHECKED"
    CLAIM_GRAPH_BUILT = "CLAIM_GRAPH_BUILT"
    EXPERIMENT_IR_COMPILED = "EXPERIMENT_IR_COMPILED"
    FEASIBILITY_VALIDATED = "FEASIBILITY_VALIDATED"
    NOVELTY_VALUE_SCORED = "NOVELTY_VALUE_SCORED"
    PROTOCOL_GENERATED = "PROTOCOL_GENERATED"
    SCHEDULED = "SCHEDULED"
    AWAITING_HUMAN_APPROVAL = "AWAITING_HUMAN_APPROVAL"
    APPROVED = "APPROVED"
    EXECUTING = "EXECUTING"
    EXECUTION_FAILED_OR_COMPLETED = "EXECUTION_FAILED_OR_COMPLETED"
    RECOVERY_APPLIED = "RECOVERY_APPLIED"
    RESULTS_COLLECTED = "RESULTS_COLLECTED"
    RESULTS_VALIDATED = "RESULTS_VALIDATED"
    RESULTS_REPAIRED = "RESULTS_REPAIRED"
    INTERPRETED = "INTERPRETED"
    NEXT_EXPERIMENT_RECOMMENDED = "NEXT_EXPERIMENT_RECOMMENDED"
    REPORT_GENERATED = "REPORT_GENERATED"
    MEMORY_UPDATED = "MEMORY_UPDATED"


STATE_SEQUENCE = [
    RunState.CREATED,
    RunState.GOAL_PARSED,
    RunState.LITERATURE_SEARCHED,
    RunState.PRIOR_WORK_MATCHED,
    RunState.NEGATIVE_RESULTS_CHECKED,
    RunState.CLAIM_GRAPH_BUILT,
    RunState.EXPERIMENT_IR_COMPILED,
    RunState.FEASIBILITY_VALIDATED,
    RunState.NOVELTY_VALUE_SCORED,
    RunState.PROTOCOL_GENERATED,
    RunState.SCHEDULED,
    RunState.AWAITING_HUMAN_APPROVAL,
    RunState.APPROVED,
    RunState.EXECUTING,
    RunState.EXECUTION_FAILED_OR_COMPLETED,
    RunState.RECOVERY_APPLIED,
    RunState.RESULTS_COLLECTED,
    RunState.RESULTS_VALIDATED,
    RunState.RESULTS_REPAIRED,
    RunState.INTERPRETED,
    RunState.NEXT_EXPERIMENT_RECOMMENDED,
    RunState.REPORT_GENERATED,
    RunState.MEMORY_UPDATED,
]


class HelixModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ExperimentRun(HelixModel):
    id: str
    title: str
    domain: str = "materials_discovery"
    state: RunState = RunState.CREATED
    user_goal: str
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    artifacts: dict[str, Any] = Field(default_factory=dict)


class ScientificIntent(HelixModel):
    domain: str
    objective: str
    base_material: str
    intervention: str
    target_property: str
    must_preserve: str
    constraints: dict[str, Any]
    success_metrics: list[str]
    primary_question: str
    search_entities: list[str]
    synonyms: dict[str, list[str]]


class LiteratureQueryPlan(HelixModel):
    exact_queries: list[str]
    broad_queries: list[str]
    negative_result_queries: list[str]
    protocol_queries: list[str]


class RetrievedPaper(HelixModel):
    paper_id: str
    title: str
    abstract: str
    authors: list[str]
    year: int | None = None
    venue: str | None = None
    doi: str | None = None
    url: str | None = None
    source: str
    retrieval_mode: str


class EvidenceSource(HelixModel):
    type: str
    title: str
    identifier: str


class ExperimentFacts(HelixModel):
    material: str
    intervention: str
    variable: str
    tested_values: list[float]
    measured_properties: list[str]
    reported_outcome: str


class MatchToHypothesis(HelixModel):
    overlap: str
    redundancy_contribution: float
    novelty_gap: str


class EvidenceExtraction(HelixModel):
    evidence_id: str
    source: EvidenceSource
    experiment_facts: ExperimentFacts
    match_to_user_hypothesis: MatchToHypothesis


class PriorMatchItem(HelixModel):
    source_type: str
    title: str | None = None
    identifier: str | None = None
    source_id: str | None = None
    overlap: str
    tested_conditions: list[str]
    reported_result: str
    evidence_strength: float


class PriorWorkMatch(HelixModel):
    prior_work_status: str
    matches: list[PriorMatchItem]
    gap: str
    recommendation: str


class NegativeResult(HelixModel):
    negative_result_id: str
    experiment: str
    failed_condition: str
    failure_type: str
    observed_result: dict[str, Any]
    recommendation: str
    source: str


class Claim(HelixModel):
    id: str
    claim: str
    status: str
    evidence: list[str]


class ClaimGraph(HelixModel):
    main_hypothesis: str
    claims: list[Claim]
    weakest_high_value_claim: str


class ExperimentIR(HelixModel):
    experiment_id: str
    domain: str
    hypothesis: str
    target_claim: str
    experiment_type: str
    material: str
    variables: dict[str, list[float]]
    controls: list[str]
    success_metrics: list[str]
    constraints: dict[str, Any]
    evidence_context: dict[str, Any]
    required_resources: list[str]
    expected_output_schema: str


class ValidationIssue(HelixModel):
    severity: str
    issue: str
    resolution: str


class FeasibilityReport(HelixModel):
    validation_status: str
    issues: list[ValidationIssue]
    approved_for_protocol_generation: bool


class ExperimentValueScore(HelixModel):
    prior_work_status: str
    redundancy_score: float
    novelty_score: float
    expected_information_gain: float
    feasibility_score: float
    resource_cost: float
    risk_score: float
    overall_experiment_value: float
    recommendation: str


class ProtocolStep(HelixModel):
    step_id: str
    name: str
    resource_type: str
    duration_minutes: int
    depends_on: list[str]


class Protocol(HelixModel):
    protocol_id: str
    name: str
    steps: list[ProtocolStep]


class LabResource(HelixModel):
    resource_id: str
    type: str
    available_at: str
    capabilities: list[str]
    status: str


class ScheduledTask(HelixModel):
    step_id: str
    resource_id: str
    start: str
    end: str


class Schedule(HelixModel):
    schedule_id: str
    scheduled_tasks: list[ScheduledTask]
    priority_score: float = 0.82


class ApprovalEvent(HelixModel):
    approval_id: str
    run_id: str
    approved: bool
    approved_by: str
    timestamp: datetime = Field(default_factory=utc_now)
    notes: str


class ExecutionEvent(HelixModel):
    timestamp: str
    step_id: str
    event_type: str
    message: str


class ExecutionLog(HelixModel):
    execution_id: str
    status: str
    events: list[ExecutionEvent]
    raw_result_csv: str


class RecoveryOption(HelixModel):
    action: str
    cost_minutes: int
    data_loss: str
    score: float


class FailureRecoveryPlan(HelixModel):
    failure_type: str
    affected_step: str
    affected_condition: str
    recovery_options: list[RecoveryOption]
    selected_recovery: str


class ResultSchemaField(HelixModel):
    name: str
    type: str


class ResultSchema(HelixModel):
    schema_id: str
    fields: list[ResultSchemaField]


class ResultValidationIssue(HelixModel):
    type: str
    expected: str
    found: str
    repair: str


class ValidationReport(HelixModel):
    valid: bool
    issues: list[ResultValidationIssue]
    repair_status: str


class RepairedResult(HelixModel):
    candidate_id: str
    mn_fraction: float
    energy_above_hull: float
    conductivity_proxy: float
    stability_pass: bool


class ResultInterpretation(HelixModel):
    observed_results: list[str]
    prior_evidence: list[str]
    inference: str
    uncertainty: str
    limitations: list[str]


class CandidateNextExperiment(HelixModel):
    name: str
    conditions: list[float]
    expected_information_gain: float
    novelty: float
    feasibility: float
    redundancy: float
    cost: float
    risk: float
    score: float


class NextExperimentRecommendation(HelixModel):
    candidate_next_experiments: list[CandidateNextExperiment]
    selected_next_experiment: str
    rationale: str


class ProvenanceEvent(HelixModel):
    event_id: str
    run_id: str
    timestamp: datetime = Field(default_factory=utc_now)
    event_type: str
    summary: str
    actor: str
    payload: dict[str, Any] = Field(default_factory=dict)


class ProvenanceReportSection(HelixModel):
    title: str
    content: str


class ProvenanceReport(HelixModel):
    run_id: str
    title: str
    sections: list[ProvenanceReportSection]
    provenance_events: list[ProvenanceEvent]

