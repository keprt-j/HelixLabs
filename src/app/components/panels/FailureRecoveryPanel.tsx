import { ArtifactJsonPanel } from "./ArtifactJsonPanel";

interface FailureRecoveryPanelProps {
  artifact?: Record<string, unknown> | null;
}

export function FailureRecoveryPanel({ artifact }: FailureRecoveryPanelProps) {
  return (
    <ArtifactJsonPanel
      artifact={artifact}
      emptyMessage="Recovery plan is recorded after the execution stage completes (including any failure path)."
      title="Failure & recovery (from run)"
    />
  );
}
