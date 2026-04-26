import { ArtifactJsonPanel } from "./ArtifactJsonPanel";

interface ExecutionPanelProps {
  artifact?: Record<string, unknown> | null;
}

export function ExecutionPanel({ artifact }: ExecutionPanelProps) {
  return (
    <ArtifactJsonPanel
      artifact={artifact}
      emptyMessage="Execution log appears after you approve the schedule and advance through execution."
      title="Execution log (from run)"
    />
  );
}
