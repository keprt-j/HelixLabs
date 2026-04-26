import type { HelixRun } from "../types/run";

function asObj(v: unknown): Record<string, unknown> | null {
  return v && typeof v === "object" && !Array.isArray(v) ? (v as Record<string, unknown>) : null;
}

export function buildDemoReport(run: HelixRun): string {
  const artifacts = asObj(run.artifacts) || {};
  const interp = asObj(artifacts.interpretation) || {};
  const next = asObj(artifacts.next_experiment_recommendation) || {};
  const normalized = asObj(artifacts.normalized_results) || {};
  const fidelity = typeof normalized.fidelity === "string" ? normalized.fidelity : "unknown";
  const origin = typeof normalized.origin === "string" ? normalized.origin : "unknown";
  const scopeNote =
    typeof (asObj(artifacts.report) || {}).scope_note === "string"
      ? String((asObj(artifacts.report) || {}).scope_note)
      : "Evidence-conditioned simulation for planning support; not a protocol-faithful replication.";
  const provenance = Array.isArray(run.provenance) ? run.provenance.slice(-5) : [];

  return [
    `# HelixLabs Demo Report`,
    ``,
    `- Run ID: ${run.run_id}`,
    `- Goal: ${run.user_goal}`,
    `- State: ${run.state}`,
    `- Fidelity: ${fidelity}`,
    `- Origin: ${origin}`,
    `- Scope: ${scopeNote}`,
    ``,
    `## Interpretation`,
    `${String(interp.inference ?? "No interpretation available.")}`,
    ``,
    `## Next Recommendation`,
    `${String(next.recommendation ?? "No recommendation available.")}`,
    ``,
    `## Recent Provenance Events`,
    ...provenance.map((e) => `- [${String(e.time)}] ${String(e.event_type)}: ${String(e.message)}`),
    ``,
  ].join("\n");
}
