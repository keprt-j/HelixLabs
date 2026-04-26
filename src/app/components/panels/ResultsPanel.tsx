import { ArtifactJsonPanel } from "./ArtifactJsonPanel";
import { ProcedureTracePanel } from "./ProcedureTracePanel";
import { Line, LineChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

interface ResultsPanelProps {
  artifact?: Record<string, unknown> | null;
  /** Surrogate σ(T) series from execution_log.series_for_charts */
  chartSeries?: Record<string, unknown> | null;
  procedureTrace?: Array<Record<string, unknown>> | null;
}

function buildChartRows(series: Record<string, unknown>): { temp: number; sigma: number }[] {
  // Legacy chemistry shape
  const temps = series.temperature_c;
  const sigs = series.sigma_S_cm;
  if (Array.isArray(temps) && Array.isArray(sigs) && temps.length === sigs.length) {
    const rows: { temp: number; sigma: number }[] = [];
    for (let i = 0; i < temps.length; i++) {
      const t = Number(temps[i]);
      const s = Number(sigs[i]);
      if (!Number.isFinite(t) || !Number.isFinite(s)) continue;
      rows.push({ temp: t, sigma: s });
    }
    return rows;
  }

  // Generic plugin shape
  const x = series.x;
  const y = series.y;
  if (!Array.isArray(x) || !Array.isArray(y) || x.length !== y.length) return [];
  const rows: { temp: number; sigma: number }[] = [];
  for (let i = 0; i < x.length; i++) {
    const t = Number(x[i]);
    const s = Number(y[i]);
    if (!Number.isFinite(t) || !Number.isFinite(s)) continue;
    rows.push({ temp: t, sigma: s });
  }
  return rows;
}

export function ResultsPanel({ artifact, chartSeries, procedureTrace }: ResultsPanelProps) {
  const label = typeof chartSeries?.label === "string" ? chartSeries.label : "Simulated σ vs temperature";
  const rows = chartSeries ? buildChartRows(chartSeries as Record<string, unknown>) : [];

  return (
    <div className="space-y-6">
      {rows.length > 0 && (
        <div className="bg-yellow-50/50 border border-amber-200 rounded-lg p-6">
          <h3 className="text-sm text-stone-600 mb-4">{label}</h3>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={rows} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#d6d3d1" />
                <XAxis dataKey="temp" name="T (°C)" tick={{ fontSize: 11 }} label={{ value: "Temperature (°C)", position: "bottom", offset: 0, fontSize: 11 }} />
                <YAxis
                  dataKey="sigma"
                  tick={{ fontSize: 11 }}
                  tickFormatter={(v) => (v < 0.01 ? v.toExponential(1) : v.toFixed(4))}
                  label={{ value: "σ (S/cm)", angle: -90, position: "insideLeft", fontSize: 11 }}
                />
                <Tooltip formatter={(v: number) => [v.toExponential(4), "σ"]} labelFormatter={(l) => `${l} °C`} />
                <Line type="monotone" dataKey="sigma" stroke="#15803d" strokeWidth={2} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <p className="text-xs text-stone-500 mt-2">
            Literature-conditioned surrogate (see execution log for raw measurements and simulation_config).
          </p>
        </div>
      )}

      <ProcedureTracePanel trace={procedureTrace} />

      <ArtifactJsonPanel
        artifact={artifact}
        emptyMessage="Interpretation is produced after the interpret stage completes."
        title="Interpretation (from run)"
      />
    </div>
  );
}
