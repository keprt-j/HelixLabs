import { ArtifactJsonPanel } from "./ArtifactJsonPanel";

interface DataValidationPanelProps {
  artifact?: Record<string, unknown> | null;
  generatedAt?: string | null;
  summary?: string | null;
}

export function DataValidationPanel({ artifact, generatedAt, summary }: DataValidationPanelProps) {
  return (
    <ArtifactJsonPanel
      artifact={artifact}
      emptyMessage="Validation report is produced after recovery and validate-results stages."
      generatedAt={generatedAt}
      summary={summary}
      title="Data validation (from run)"
    />
  );
}
