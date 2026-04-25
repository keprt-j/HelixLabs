export type RunState =
  | "CREATED"
  | "GOAL_PARSED"
  | "LITERATURE_SEARCHED"
  | "PRIOR_WORK_MATCHED"
  | "NEGATIVE_RESULTS_CHECKED"
  | "CLAIM_GRAPH_BUILT"
  | "EXPERIMENT_IR_COMPILED"
  | "FEASIBILITY_VALIDATED"
  | "NOVELTY_VALUE_SCORED"
  | "PROTOCOL_GENERATED"
  | "SCHEDULED"
  | "AWAITING_HUMAN_APPROVAL"
  | "APPROVED"
  | "EXECUTING"
  | "EXECUTION_FAILED_OR_COMPLETED"
  | "RECOVERY_APPLIED"
  | "RESULTS_COLLECTED"
  | "RESULTS_VALIDATED"
  | "RESULTS_REPAIRED"
  | "INTERPRETED"
  | "NEXT_EXPERIMENT_RECOMMENDED"
  | "REPORT_GENERATED"
  | "MEMORY_UPDATED";

export const stateSequence: RunState[] = [
  "CREATED",
  "GOAL_PARSED",
  "LITERATURE_SEARCHED",
  "PRIOR_WORK_MATCHED",
  "NEGATIVE_RESULTS_CHECKED",
  "CLAIM_GRAPH_BUILT",
  "EXPERIMENT_IR_COMPILED",
  "FEASIBILITY_VALIDATED",
  "NOVELTY_VALUE_SCORED",
  "PROTOCOL_GENERATED",
  "SCHEDULED",
  "AWAITING_HUMAN_APPROVAL",
  "APPROVED",
  "EXECUTING",
  "EXECUTION_FAILED_OR_COMPLETED",
  "RECOVERY_APPLIED",
  "RESULTS_COLLECTED",
  "RESULTS_VALIDATED",
  "RESULTS_REPAIRED",
  "INTERPRETED",
  "NEXT_EXPERIMENT_RECOMMENDED",
  "REPORT_GENERATED",
  "MEMORY_UPDATED"
];

export type RunPayload = {
  run: {
    id: string;
    title: string;
    domain: string;
    state: RunState;
    user_goal: string;
    created_at: string;
    updated_at: string;
  };
  artifacts: Record<string, any>;
  provenance_events: Array<{
    event_id: string;
    event_type: string;
    summary: string;
    actor: string;
    timestamp: string;
    payload: Record<string, any>;
  }>;
};

