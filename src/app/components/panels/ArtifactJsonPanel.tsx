/** Shows server artifact JSON or a short empty-state hint. */
export function ArtifactJsonPanel({
  artifact,
  emptyMessage,
  title,
}: {
  artifact: Record<string, unknown> | null | undefined;
  emptyMessage: string;
  title?: string;
}) {
  if (!artifact || Object.keys(artifact).length === 0) {
    return (
      <div className="rounded-lg border border-amber-200 bg-yellow-50/50 p-6 text-sm text-stone-600">{emptyMessage}</div>
    );
  }

  return (
    <div className="space-y-3">
      {title ? <h3 className="text-sm text-stone-600">{title}</h3> : null}
      <pre className="text-xs text-stone-800 bg-white/70 border border-amber-200 rounded-lg p-4 overflow-x-auto max-h-[480px]">
        {JSON.stringify(artifact, null, 2)}
      </pre>
    </div>
  );
}
