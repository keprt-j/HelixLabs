import { ArtifactJsonPanel } from "./ArtifactJsonPanel";

interface DataValidationPanelProps {
  artifact?: Record<string, unknown> | null;
}

export function DataValidationPanel({ artifact }: DataValidationPanelProps) {
  return (
    <ArtifactJsonPanel
      artifact={artifact}
      emptyMessage="Validation report is produced after recovery and validate-results stages."
      title="Data validation (from run)"
    />
  );
}
