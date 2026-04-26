interface ExperimentBriefPanelProps {
  run: {
    run_id: string;
    user_goal: string;
    artifacts?: Record<string, unknown>;
  };
}

function asObj(v: unknown): Record<string, unknown> | null {
  return v && typeof v === "object" && !Array.isArray(v) ? (v as Record<string, unknown>) : null;
}

export function ExperimentBriefPanel({ run }: ExperimentBriefPanelProps) {
  const artifacts = run.artifacts || {};
  const expIrWrap = asObj(artifacts.experiment_ir);
  const expIr = asObj(expIrWrap?.experiment_ir) || {};
  const plugin = asObj(expIrWrap?.plugin) || {};
  const simOverrides = asObj(artifacts.simulation_overrides) || {};

  const factors = Array.isArray(expIr.factors) ? expIr.factors.slice(0, 6) : [];
  const responses = Array.isArray(expIr.responses) ? expIr.responses.slice(0, 4) : [];
  const constraints = Array.isArray(expIr.constraints) ? expIr.constraints.slice(0, 4) : [];

  return (
    <div className="rounded-xl border border-amber-200 bg-yellow-50/60 p-5 space-y-4">
      <div className="flex items-start justify-between gap-3 flex-wrap">
        <div>
          <h3 className="text-sm text-stone-600 mb-1">Experiment Brief</h3>
          <div className="text-base text-stone-900">{run.user_goal}</div>
        </div>
        <div className="text-xs font-mono text-stone-600">
          {run.run_id}
          <div className="mt-1">plugin: {String(plugin.selected_plugin ?? "unknown")}</div>
          <div>confidence: {plugin.selection_confidence == null ? "—" : Number(plugin.selection_confidence).toFixed(2)}</div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
        <div className="rounded border border-amber-200 bg-white/70 p-3">
          <div className="text-xs text-stone-500 mb-2">Factors we are varying</div>
          {factors.length === 0 ? (
            <div className="text-stone-600">No factor metadata yet.</div>
          ) : (
            <ul className="space-y-1 text-stone-800">
              {factors.map((f, i) => {
                const row = asObj(f) || {};
                return <li key={i}>• {String(row.name ?? "factor")} ({String(row.type ?? "?")})</li>;
              })}
            </ul>
          )}
        </div>

        <div className="rounded border border-amber-200 bg-white/70 p-3">
          <div className="text-xs text-stone-500 mb-2">Responses we optimize</div>
          {responses.length === 0 ? (
            <div className="text-stone-600">No response metadata yet.</div>
          ) : (
            <ul className="space-y-1 text-stone-800">
              {responses.map((r, i) => {
                const row = asObj(r) || {};
                return <li key={i}>• {String(row.name ?? "response")} ({String(row.objective ?? "target")})</li>;
              })}
            </ul>
          )}
        </div>

        <div className="rounded border border-amber-200 bg-white/70 p-3">
          <div className="text-xs text-stone-500 mb-2">Constraints</div>
          {constraints.length === 0 ? (
            <div className="text-stone-600">No explicit constraints provided.</div>
          ) : (
            <ul className="space-y-1 text-stone-800">
              {constraints.map((c, i) => {
                const row = asObj(c) || {};
                return <li key={i}>• {String(row.expression ?? "constraint")}</li>;
              })}
            </ul>
          )}
        </div>
      </div>

      <div className="rounded border border-amber-200 bg-white/70 p-3 text-xs text-stone-700">
        <div className="text-xs text-stone-500 mb-1">Simulation controls</div>
        <div>
          replicates={String(simOverrides.n_replicates ?? "default")} · noise={String(simOverrides.noise_scale_relative ?? "default")} · density={String(simOverrides.design_density ?? "default")}
        </div>
      </div>
    </div>
  );
}
