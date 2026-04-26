export type HeaderWorkflowStatus = "Draft" | "Scheduled" | "Running" | "Failed" | "Completed";

export function mapRunStateToHeaderStatus(state: string): HeaderWorkflowStatus {
  if (state === "MEMORY_UPDATED" || state === "REPORT_GENERATED") {
    return "Completed";
  }
  if (state === "EXECUTION_FAILED_OR_COMPLETED") {
    return "Failed";
  }
  if (state === "AWAITING_HUMAN_APPROVAL") {
    return "Scheduled";
  }
  const draftish = new Set([
    "CREATED",
    "GOAL_PARSED",
    "LITERATURE_SEARCHED",
    "PRIOR_WORK_MATCHED",
    "NEGATIVE_RESULTS_CHECKED",
    "CLAIM_GRAPH_BUILT",
  ]);
  if (draftish.has(state)) {
    return "Draft";
  }
  return "Running";
}
