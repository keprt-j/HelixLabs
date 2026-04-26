import { PipelineJsonInspector } from "./PipelineJsonInspector";

/** Shows server artifact JSON behind a collapsible, summary-first inspector. */
export function ArtifactJsonPanel({
  artifact,
  emptyMessage,
  generatedAt,
  summary,
  title,
}: {
  artifact: Record<string, unknown> | null | undefined;
  emptyMessage: string;
  generatedAt?: string | null;
  summary?: string | null;
  title?: string;
}) {
  if (!artifact || Object.keys(artifact).length === 0) {
    return (
      <div className="rounded-lg border border-amber-200 bg-yellow-50/50 p-6 text-sm text-stone-600">{emptyMessage}</div>
    );
  }

  return (
    <PipelineJsonInspector
      title={title ?? "Artifact JSON"}
      summary={summary}
      generatedAt={generatedAt}
      data={artifact}
    />
  );
}
