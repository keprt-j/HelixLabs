import { describe, expect, it } from "vitest";
import { buildDemoReport } from "./demoReport";

describe("buildDemoReport", () => {
  it("includes core run metadata and interpretation", () => {
    const report = buildDemoReport({
      run_id: "RUN-1",
      user_goal: "Optimize yield",
      state: "REPORT_GENERATED",
      pipeline: { intake: { parsed_goal: {}, literature: {}, prior_work: {}, claim_graph: {} }, planning: { compiler: {}, schedule: {} }, runtime: {}, outcomes: {} },
      artifacts: {
        interpretation: { inference: "Yield increased." },
        next_experiment_recommendation: { recommendation: "Try higher catalyst." },
        normalized_results: { fidelity: "medium", origin: "simulated" },
      },
      provenance: [{ time: "t", event_type: "STATE", category: "Runtime", message: "Done" }],
      created_at: "c",
      updated_at: "u",
    });
    expect(report).toContain("RUN-1");
    expect(report).toContain("Yield increased.");
    expect(report).toContain("Try higher catalyst.");
  });
});
