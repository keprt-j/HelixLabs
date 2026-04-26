export type PipelineStage = "intake" | "planning" | "runtime" | "outcomes";

export interface RunContract {
  run_id: string;
  user_goal: string;
  state:
    | "INTAKE_COMPLETE"
    | "PLANNING_COMPLETE"
    | "RUNTIME_COMPLETE"
    | "OUTCOMES_COMPLETE";
  pipeline: {
    intake: Record<string, unknown>;
    planning: Record<string, unknown>;
    runtime: Record<string, unknown>;
    outcomes: Record<string, unknown>;
  };
  updated_at: string;
}
