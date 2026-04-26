import { ArtifactJsonPanel } from "./ArtifactJsonPanel";

interface ExecutionPanelProps {
  artifact?: Record<string, unknown> | null;
  generatedAt?: string | null;
  summary?: string | null;
}

export function ExecutionPanel({ artifact, generatedAt, summary }: ExecutionPanelProps) {
  return (
    <ArtifactJsonPanel
      artifact={artifact}
      emptyMessage="Execution log appears after you approve the schedule and advance through execution."
      generatedAt={generatedAt}
      summary={summary}
      title="Execution log (from run)"
    />
  );
}
