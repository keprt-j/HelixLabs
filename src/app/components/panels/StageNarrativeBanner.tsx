interface StageNarrativeBannerProps {
  section: "intake" | "planning" | "runtime" | "outcomes";
  tab: string;
}

const COPY: Record<string, string[]> = {
  "intake:goal": [
    "Translate your objective into a structured experiment intent.",
    "Extract entities and constraints that shape downstream design.",
  ],
  "intake:prior-work": [
    "Compare retrieved evidence against your objective.",
    "Estimate novelty/redundancy to avoid repeating known work.",
  ],
  "intake:claim-graph": [
    "Identify strongest and weakest claims from the evidence bundle.",
    "Choose the next target claim to test experimentally.",
  ],
  "planning:compiler": [
    "Compile universal Experiment IR (factors, responses, constraints, procedure).",
    "Validate IR for semantic consistency before execution.",
  ],
  "planning:schedule": [
    "Estimate execution workload and expected resource footprint.",
    "Prepare approval-ready plan before runtime begins.",
  ],
  "runtime:execution": [
    "Execute design points using selected plugin backend.",
    "Emit normalized observations and chart-ready series.",
  ],
  "runtime:recovery": [
    "Detect adverse conditions and apply recovery policy.",
    "Record adjustments in the procedural trace.",
  ],
  "runtime:validation": [
    "Validate output schema and mapped columns.",
    "Mark data quality checks before interpretation.",
  ],
  "runtime:results": [
    "Visualize measured trends and exploratory statistics.",
    "Inspect assumptions through fidelity and origin labels.",
  ],
  "outcomes:summary": [
    "Summarize goal, plugin selection, and evidence of execution.",
    "Provide executive context before deeper inspection.",
  ],
  "outcomes:next": [
    "Recommend the next experiment from observed outcomes.",
    "Quantify information gain and operational risk.",
  ],
  "outcomes:provenance": [
    "Show full event trace of model, decision, and state transitions.",
    "Support auditability and reproducibility review.",
  ],
  "outcomes:compare": [
    "Compare two runs side-by-side to understand strategy drift.",
    "Inspect plugin choice, observations, and best-condition deltas.",
  ],
};

export function StageNarrativeBanner({ section, tab }: StageNarrativeBannerProps) {
  const lines = COPY[`${section}:${tab}`] ?? ["Process details will appear as this stage executes."];
  return (
    <div className="rounded-lg border border-blue-200 bg-blue-50/60 p-4">
      <div className="text-xs text-blue-700 mb-1 uppercase tracking-wide">What this step is doing</div>
      <ul className="text-sm text-blue-900 space-y-1">
        {lines.map((line) => (
          <li key={line}>• {line}</li>
        ))}
      </ul>
    </div>
  );
}
