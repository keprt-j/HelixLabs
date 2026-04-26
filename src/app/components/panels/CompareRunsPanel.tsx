import { useEffect, useMemo, useState } from "react";
import type { HelixRun, RunListItem } from "../../types/run";
import { fetchRun, fetchRunList } from "../../api/runApi";

interface CompareRunsPanelProps {
  baseRun: HelixRun | null;
}

function getMetric(run: HelixRun | null, key: string): string {
  if (!run) return "—";
  const norm = (run.artifacts?.normalized_results as Record<string, unknown> | undefined) || {};
  const summary = (norm.summary_metrics as Record<string, unknown> | undefined) || {};
  const best = (summary.best_condition as Record<string, unknown> | undefined) || {};
  const plugin = ((run.artifacts?.experiment_ir as Record<string, unknown> | undefined)?.plugin as Record<string, unknown> | undefined) || {};
  if (key === "plugin") return String(plugin.selected_plugin ?? "—");
  if (key === "state") return run.state;
  if (key === "obs") return String(Array.isArray(norm.observations) ? norm.observations.length : 0);
  if (key === "best") return JSON.stringify(best);
  return "—";
}

export function CompareRunsPanel({ baseRun }: CompareRunsPanelProps) {
  const [runs, setRuns] = useState<RunListItem[]>([]);
  const [selected, setSelected] = useState<string>("");
  const [compareRun, setCompareRun] = useState<HelixRun | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void (async () => {
      try {
        const list = await fetchRunList(100);
        setRuns(list);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load run list");
      }
    })();
  }, []);

  useEffect(() => {
    if (!selected) {
      setCompareRun(null);
      return;
    }
    void (async () => {
      try {
        const run = await fetchRun(selected);
        setCompareRun(run);
        setError(null);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load comparison run");
      }
    })();
  }, [selected]);

  const options = useMemo(
    () => runs.filter((r) => r.run_id !== baseRun?.run_id),
    [runs, baseRun?.run_id],
  );

  const rows = [
    { label: "Run ID", a: baseRun?.run_id ?? "—", b: compareRun?.run_id ?? "—" },
    { label: "State", a: getMetric(baseRun, "state"), b: getMetric(compareRun, "state") },
    { label: "Plugin", a: getMetric(baseRun, "plugin"), b: getMetric(compareRun, "plugin") },
    { label: "Observations", a: getMetric(baseRun, "obs"), b: getMetric(compareRun, "obs") },
    { label: "Best condition", a: getMetric(baseRun, "best"), b: getMetric(compareRun, "best") },
  ];

  return (
    <div className="bg-yellow-50/50 border border-amber-200 rounded-lg p-6 space-y-4">
      <h3 className="text-sm text-stone-600">Compare runs</h3>
      <div className="flex flex-col gap-2">
        <label className="text-xs text-stone-500">Select run to compare against current run</label>
        <select
          value={selected}
          onChange={(e) => setSelected(e.target.value)}
          className="px-3 py-2 rounded border border-amber-200 bg-white/80 text-sm"
        >
          <option value="">Choose run...</option>
          {options.map((r) => (
            <option key={r.run_id} value={r.run_id}>
              {r.run_id} · {r.state} · {r.user_goal.slice(0, 72)}
            </option>
          ))}
        </select>
      </div>
      {error && <div className="text-sm text-red-700">{error}</div>}

      <div className="overflow-auto rounded border border-amber-200 bg-white/80">
        <table className="min-w-full text-sm">
          <thead className="bg-amber-100/70">
            <tr>
              <th className="text-left px-3 py-2">Metric</th>
              <th className="text-left px-3 py-2">Current</th>
              <th className="text-left px-3 py-2">Comparison</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.label} className="border-t border-amber-100">
                <td className="px-3 py-2 text-stone-600">{r.label}</td>
                <td className="px-3 py-2 text-stone-900 font-mono text-xs">{r.a}</td>
                <td className="px-3 py-2 text-stone-900 font-mono text-xs">{r.b}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
