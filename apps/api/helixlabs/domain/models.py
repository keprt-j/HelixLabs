from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


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


class ProvenanceEvent(BaseModel):
    time: str
    event_type: str
    category: str
    message: str


class FactorType(str, Enum):
    CONTINUOUS = "continuous"
    CATEGORICAL = "categorical"
    ORDINAL = "ordinal"
    BOOLEAN = "boolean"


class ResponseObjective(str, Enum):
    MAXIMIZE = "maximize"
    MINIMIZE = "minimize"
    TARGET = "target"


class FactorSpec(BaseModel):
    name: str = Field(min_length=1)
    type: FactorType
    units: str | None = None
    bounds: dict[str, float] | None = None
    levels: list[str | float | bool] = Field(default_factory=list)


class ResponseSpec(BaseModel):
    name: str = Field(min_length=1)
    objective: ResponseObjective
    target_value: float | None = None
    units: str | None = None
    valid_range: dict[str, float] | None = None


class ConstraintSpec(BaseModel):
    expression: str = Field(min_length=1)
    severity: str = "hard"


class ProcedureStep(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str | None = None
    expected_outputs: list[str] = Field(default_factory=list)


class ExperimentIR(BaseModel):
    version: str = "1.0"
    domain_hint: str | None = None
    hypothesis: dict[str, Any]
    factors: list[FactorSpec]
    responses: list[ResponseSpec]
    constraints: list[ConstraintSpec] = Field(default_factory=list)
    design: dict[str, Any]
    procedure_steps: list[ProcedureStep]
    analysis_plan: dict[str, Any] = Field(default_factory=dict)
    provenance_refs: list[str] = Field(default_factory=list)


class IntakePayload(BaseModel):
    parsed_goal: dict[str, Any]
    literature: dict[str, Any]
    prior_work: dict[str, Any]
    claim_graph: dict[str, Any]


class PlanningPayload(BaseModel):
    compiler: dict[str, Any]
    schedule: dict[str, Any]


class RuntimePayload(BaseModel):
    execution: dict[str, Any]
    recovery: dict[str, Any]
    validation: dict[str, Any]
    results: dict[str, Any]


class OutcomesPayload(BaseModel):
    next_experiment: dict[str, Any]
    report: dict[str, Any]


class PipelinePayload(BaseModel):
    intake: IntakePayload = Field(default_factory=lambda: IntakePayload(parsed_goal={}, literature={}, prior_work={}, claim_graph={}))
    planning: PlanningPayload = Field(default_factory=lambda: PlanningPayload(compiler={}, schedule={}))
    runtime: RuntimePayload = Field(default_factory=lambda: RuntimePayload(execution={}, recovery={}, validation={}, results={}))
    outcomes: OutcomesPayload = Field(default_factory=lambda: OutcomesPayload(next_experiment={}, report={}))


class RunRecord(BaseModel):
    run_id: str
    user_goal: str
    state: RunState
    pipeline: PipelinePayload
    artifacts: dict[str, Any] = Field(default_factory=dict)
    provenance: list[ProvenanceEvent] = Field(default_factory=list)
    created_at: str
    updated_at: str

    @staticmethod
    def now_iso() -> str:
        return datetime.now(tz=timezone.utc).isoformat()
