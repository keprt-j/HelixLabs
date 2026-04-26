interface RunSummaryPanelProps {
  run: {
    run_id: string;
    user_goal: string;
    state: string;
    updated_at: string;
    artifacts?: Record<string, unknown>;
  };
}

export function RunSummaryPanel({ run }: RunSummaryPanelProps) {
  const artifacts = run.artifacts || {};
  const ir = (artifacts.experiment_ir as Record<string, unknown> | undefined) || {};
  const plugin = ((ir.plugin as Record<string, unknown> | undefined)?.selected_plugin as string | undefined) ?? "unknown";
  const conf = ((ir.plugin as Record<string, unknown> | undefined)?.selection_confidence as number | undefined) ?? null;
  const norm = (artifacts.normalized_results as Record<string, unknown> | undefined) || {};
  const obs = Array.isArray(norm.observations) ? norm.observations.length : 0;
  const series = Array.isArray(norm.series) ? norm.series.length : 0;

  return (
    <div className="bg-yellow-50/50 border border-amber-200 rounded-lg p-6 space-y-4">
      <div>
        <h3 className="text-sm text-stone-600 mb-1">Run summary</h3>
        <div className="text-sm text-stone-900 font-mono">{run.run_id}</div>
        <p className="text-sm text-stone-700 mt-2">{run.user_goal}</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="p-3 rounded border border-amber-200 bg-white/70">
          <div className="text-xs text-stone-500">State</div>
          <div className="text-sm text-stone-900 font-medium">{run.state}</div>
        </div>
        <div className="p-3 rounded border border-amber-200 bg-white/70">
          <div className="text-xs text-stone-500">Plugin</div>
          <div className="text-sm text-stone-900 font-medium">{plugin}</div>
        </div>
        <div className="p-3 rounded border border-amber-200 bg-white/70">
          <div className="text-xs text-stone-500">Confidence</div>
          <div className="text-sm text-stone-900 font-medium">{conf == null ? "—" : conf.toFixed(2)}</div>
        </div>
        <div className="p-3 rounded border border-amber-200 bg-white/70">
          <div className="text-xs text-stone-500">Updated</div>
          <div className="text-sm text-stone-900 font-medium">{new Date(run.updated_at).toLocaleString()}</div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="p-3 rounded border border-amber-200 bg-white/70">
          <div className="text-xs text-stone-500">Observations</div>
          <div className="text-xl text-stone-900">{obs}</div>
        </div>
        <div className="p-3 rounded border border-amber-200 bg-white/70">
          <div className="text-xs text-stone-500">Series</div>
          <div className="text-xl text-stone-900">{series}</div>
        </div>
      </div>
    </div>
  );
}
