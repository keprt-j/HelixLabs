import { ArtifactJsonPanel } from "./ArtifactJsonPanel";

interface FailureRecoveryPanelProps {
  artifact?: Record<string, unknown> | null;
  generatedAt?: string | null;
  summary?: string | null;
}

export function FailureRecoveryPanel({ artifact, generatedAt, summary }: FailureRecoveryPanelProps) {
  return (
    <ArtifactJsonPanel
      artifact={artifact}
      emptyMessage="Recovery plan is recorded after the execution stage completes (including any failure path)."
      generatedAt={generatedAt}
      summary={summary}
      title="Failure & recovery (from run)"
    />
  );
}
