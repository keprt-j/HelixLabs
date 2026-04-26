export type HelixRun = {
  run_id: string;
  user_goal: string;
  state: string;
  pipeline: {
    intake: {
      parsed_goal: Record<string, unknown>;
      literature: Record<string, unknown>;
      prior_work: Record<string, unknown>;
      claim_graph: Record<string, unknown>;
    };
    planning: { compiler: Record<string, unknown>; schedule: Record<string, unknown> };
    runtime: Record<string, unknown>;
    outcomes: Record<string, unknown>;
  };
  artifacts: Record<string, unknown>;
  provenance: Array<{ time: string; event_type: string; category: string; message: string }>;
  created_at: string;
  updated_at: string;
};

export type RunListItem = {
  run_id: string;
  state: string;
  user_goal: string;
  updated_at: string;
};
