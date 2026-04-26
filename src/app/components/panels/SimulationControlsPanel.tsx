import { useMemo, useState } from "react";
import type { SimulationOverrides } from "../../api/runApi";

interface SimulationControlsPanelProps {
  current?: Record<string, unknown> | null;
  onApply: (overrides: SimulationOverrides) => void | Promise<void>;
  busy?: boolean;
}

function asNumber(v: unknown, fallback: number): number {
  const n = Number(v);
  return Number.isFinite(n) ? n : fallback;
}

export function SimulationControlsPanel({ current, onApply, busy }: SimulationControlsPanelProps) {
  const initial = useMemo(() => {
    const c = current ?? {};
    const density = String(c.design_density ?? "medium");
    return {
      replicates: Math.max(1, Math.min(20, Math.round(asNumber(c.n_replicates, 1)))),
      noise: Math.max(0, Math.min(0.25, asNumber(c.noise_scale_relative, 0.06))),
      density: density === "coarse" || density === "fine" ? density : "medium",
    };
  }, [current]);

  const [replicates, setReplicates] = useState(initial.replicates);
  const [noise, setNoise] = useState(initial.noise);
  const [density, setDensity] = useState<"coarse" | "medium" | "fine">(initial.density as "coarse" | "medium" | "fine");

  return (
    <div className="rounded-lg border border-amber-200 bg-yellow-50/50 p-6 space-y-4">
      <h3 className="text-sm text-stone-700">Simulation Controls (Planning)</h3>
      <p className="text-xs text-stone-600">
        Tune these before execution. Applying controls will regenerate planning artifacts from IR through schedule.
      </p>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
        <label className="rounded border border-amber-200 bg-white/70 p-3">
          <div className="text-stone-700 mb-1">Replicates / condition</div>
          <select
            className="w-full rounded border border-amber-200 bg-white px-2 py-1 text-stone-900"
            value={replicates}
            onChange={(e) => setReplicates(Number(e.target.value))}
          >
            <option value={1}>1</option>
            <option value={3}>3</option>
            <option value={5}>5</option>
          </select>
        </label>
        <label className="rounded border border-amber-200 bg-white/70 p-3">
          <div className="text-stone-700 mb-1">Noise level</div>
          <select
            className="w-full rounded border border-amber-200 bg-white px-2 py-1 text-stone-900"
            value={noise}
            onChange={(e) => setNoise(Number(e.target.value))}
          >
            <option value={0.03}>Low</option>
            <option value={0.06}>Medium</option>
            <option value={0.1}>High</option>
          </select>
        </label>
        <label className="rounded border border-amber-200 bg-white/70 p-3">
          <div className="text-stone-700 mb-1">Design density</div>
          <select
            className="w-full rounded border border-amber-200 bg-white px-2 py-1 text-stone-900"
            value={density}
            onChange={(e) => setDensity(e.target.value as "coarse" | "medium" | "fine")}
          >
            <option value="coarse">Coarse (fewer trials)</option>
            <option value="medium">Medium</option>
            <option value="fine">Fine (more trials)</option>
          </select>
        </label>
      </div>
      <button
        type="button"
        disabled={busy}
        onClick={() => onApply({ n_replicates: replicates, noise_scale_relative: noise, design_density: density })}
        className="px-4 py-2 bg-green-700 hover:bg-green-800 disabled:opacity-50 text-white rounded text-sm"
      >
        Apply Controls & Replan
      </button>
    </div>
  );
}
