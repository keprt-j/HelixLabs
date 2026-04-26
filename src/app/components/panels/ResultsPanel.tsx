import { useMemo, useState } from "react";
import { ArtifactJsonPanel } from "./ArtifactJsonPanel";
import { ProcedureTracePanel } from "./ProcedureTracePanel";
import { ObservationsTablePanel } from "./ObservationsTablePanel";
import { Line, LineChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { inferSeriesKeys } from "../../lib/chartBinding";
import { computeMae, parseCsvPairs, type XYRow } from "../../lib/csvSeries";

interface ResultsPanelProps {
  artifact?: Record<string, unknown> | null;
  /** Dynamic chart series from execution_log.series_for_charts */
  chartSeries?: Record<string, unknown> | null;
  procedureTrace?: Array<Record<string, unknown>> | null;
  observations?: Array<Record<string, unknown>> | null;
  fidelity?: string | null;
  origin?: string | null;
}

type YFormat = "auto" | "scientific" | "percent" | "currency" | "integer" | "float";

type ChartModel = {
  rows: Array<{ x: string | number; y: number; yFit?: number | null }>;
  xLabel: string;
  yLabel: string;
  xUnit?: string;
  yUnit?: string;
  yFormat: YFormat;
};

type AxisDomain = [number, number] | undefined;

function toNumeric(v: unknown): number | null {
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

function toScalar(v: unknown): string | number | null {
  if (typeof v === "number" && Number.isFinite(v)) return v;
  if (typeof v === "string") return v;
  return null;
}

function parseUnitFromLabel(label: string): { base: string; unit?: string } {
  const match = label.match(/^(.*)\(([^)]+)\)\s*$/);
  if (!match) return { base: label.trim() };
  return { base: match[1].trim(), unit: match[2].trim() };
}

function withUnit(label: string, unit?: string): string {
  return unit ? `${label} (${unit})` : label;
}

function normalizeYFormat(raw: unknown): YFormat {
  const v = typeof raw === "string" ? raw.toLowerCase().trim() : "";
  if (v === "scientific" || v === "percent" || v === "currency" || v === "integer" || v === "float") {
    return v;
  }
  return "auto";
}

function inferYFormat(yLabel: string, rows: Array<{ y: number }>): YFormat {
  const l = yLabel.toLowerCase();
  if (l.includes("%") || l.includes("percent") || l.includes("rate")) return "percent";
  if (l.includes("$") || l.includes("usd") || l.includes("cost") || l.includes("revenue")) return "currency";
  const maxAbs = rows.reduce((m, r) => Math.max(m, Math.abs(r.y)), 0);
  if (maxAbs >= 1_000_000 || (maxAbs > 0 && maxAbs < 0.001)) return "scientific";
  if (rows.every((r) => Number.isInteger(r.y))) return "integer";
  return "float";
}

function formatYValue(v: number, fmt: YFormat): string {
  switch (fmt) {
    case "scientific":
      return v.toExponential(3);
    case "percent":
      return `${(v * 100).toFixed(2)}%`;
    case "currency":
      return new Intl.NumberFormat(undefined, { style: "currency", currency: "USD", maximumFractionDigits: 2 }).format(v);
    case "integer":
      return Math.round(v).toString();
    case "float":
      return Math.abs(v) < 0.01 ? v.toExponential(2) : v.toFixed(4);
    default:
      return Math.abs(v) < 0.01 ? v.toExponential(2) : v.toFixed(4);
  }
}

function buildChartModel(series: Record<string, unknown>): ChartModel | null {
  const keys = inferSeriesKeys(series);
  if (!keys) return null;
  const xArr = series[keys.xKey] as unknown[];
  const yArr = series[keys.yKey] as unknown[];
  const rows: Array<{ x: string | number; y: number; yFit?: number | null }> = [];
  for (let i = 0; i < xArr.length; i++) {
    const x = toScalar(xArr[i]);
    const y = toNumeric(yArr[i]);
    if (x === null || y === null) continue;
    rows.push({ x, y });
  }
  if (rows.length === 0) return null;
  const rawXLabel = typeof series.x_label === "string" ? series.x_label : keys.xKey;
  const rawYLabel = typeof series.y_label === "string" ? series.y_label : keys.yKey;
  const xUnit = typeof series.x_unit === "string" ? series.x_unit : undefined;
  const yUnit = typeof series.y_unit === "string" ? series.y_unit : undefined;
  const parsedX = parseUnitFromLabel(rawXLabel);
  const parsedY = parseUnitFromLabel(rawYLabel);
  const xLabel = parsedX.base || rawXLabel;
  const yLabel = parsedY.base || rawYLabel;
  const configured = normalizeYFormat(series.y_format);
  const yFormat = configured === "auto" ? inferYFormat(yLabel, rows) : configured;
  return { rows, xLabel, yLabel, xUnit: xUnit ?? parsedX.unit, yUnit: yUnit ?? parsedY.unit, yFormat };
}

function computeLinearRegression(rows: Array<{ x: string | number; y: number }>): {
  n: number;
  slope: number;
  intercept: number;
  r2: number;
} | null {
  const points = rows
    .map((r) => ({ x: typeof r.x === "number" ? r.x : Number.NaN, y: r.y }))
    .filter((p) => Number.isFinite(p.x) && Number.isFinite(p.y));
  if (points.length < 3) return null;
  const n = points.length;
  const meanX = points.reduce((s, p) => s + p.x, 0) / n;
  const meanY = points.reduce((s, p) => s + p.y, 0) / n;

  let num = 0;
  let den = 0;
  for (const p of points) {
    num += (p.x - meanX) * (p.y - meanY);
    den += (p.x - meanX) ** 2;
  }
  if (den === 0) return null;
  const slope = num / den;
  const intercept = meanY - slope * meanX;

  let ssRes = 0;
  let ssTot = 0;
  for (const p of points) {
    const pred = slope * p.x + intercept;
    ssRes += (p.y - pred) ** 2;
    ssTot += (p.y - meanY) ** 2;
  }
  const r2 = ssTot > 0 ? 1 - ssRes / ssTot : 0;
  return { n, slope, intercept, r2 };
}

function applyRegressionLine(
  rows: Array<{ x: string | number; y: number; yFit?: number | null }>,
  regression: { slope: number; intercept: number } | null,
): Array<{ x: string | number; y: number; yFit?: number | null }> {
  if (!regression) return rows.map((r) => ({ ...r, yFit: null }));
  return rows.map((r) => {
    if (typeof r.x !== "number") return { ...r, yFit: null };
    return { ...r, yFit: regression.slope * r.x + regression.intercept };
  });
}

function paddedDomain(values: number[], padFraction = 0.08): AxisDomain {
  if (values.length === 0) return undefined;
  let min = Math.min(...values);
  let max = Math.max(...values);
  if (!Number.isFinite(min) || !Number.isFinite(max)) return undefined;
  if (min === max) {
    const pad = Math.max(1e-6, Math.abs(min) * 0.1 || 0.1);
    return [min - pad, max + pad];
  }
  const span = max - min;
  const pad = Math.max(1e-6, span * padFraction);
  min -= pad;
  max += pad;
  return [min, max];
}

export function ResultsPanel({ artifact, chartSeries, procedureTrace, observations, fidelity, origin }: ResultsPanelProps) {
  const [uploaded, setUploaded] = useState<XYRow[]>([]);
  const label = typeof chartSeries?.label === "string" ? chartSeries.label : "Simulated series";
  const chart = chartSeries ? buildChartModel(chartSeries as Record<string, unknown>) : null;
  const rows = chart?.rows ?? [];
  const xLabel = chart?.xLabel ?? "x";
  const yLabel = chart?.yLabel ?? "y";
  const xUnit = chart?.xUnit;
  const yUnit = chart?.yUnit;
  const xLabelDisplay = withUnit(xLabel, xUnit);
  const yLabelDisplay = withUnit(yLabel, yUnit);
  const yFormat = chart?.yFormat ?? "float";
  const regression = computeLinearRegression(rows);
  const plotRows = applyRegressionLine(rows, regression);
  const mae = computeMae(
    plotRows.map((r) => ({ x: r.x, y: r.y })),
    uploaded,
  );
  const mergedRows = useMemo(() => {
    const map = new Map<string, { x: string | number; y: number; yFit?: number | null; yUploaded?: number | null }>();
    for (const r of plotRows) map.set(String(r.x), { ...r, yUploaded: null });
    for (const r of uploaded) {
      const k = String(r.x);
      const existing = map.get(k);
      if (existing) existing.yUploaded = r.y;
      else map.set(k, { x: r.x, y: Number.NaN, yFit: null, yUploaded: r.y });
    }
    return [...map.values()];
  }, [plotRows, uploaded]);

  const numericX = mergedRows
    .map((r) => (typeof r.x === "number" && Number.isFinite(r.x) ? r.x : null))
    .filter((v): v is number => v !== null);
  const xDomain = paddedDomain(numericX, 0.03);
  const xIsNumeric = numericX.length === mergedRows.length && mergedRows.length > 0;
  const numericY = mergedRows
    .flatMap((r) => [r.y, r.yFit, r.yUploaded])
    .map((v) => Number(v))
    .filter((v) => Number.isFinite(v));
  const yDomain = paddedDomain(numericY, 0.1);

  return (
    <div className="space-y-6">
      {rows.length > 0 && (
        <div className="bg-yellow-50/50 border border-amber-200 rounded-lg p-6">
          <div className="flex items-center justify-between gap-2 mb-4">
            <h3 className="text-sm text-stone-600">{label}</h3>
            <div className="flex items-center gap-2 text-[11px]">
              {origin ? <span className="px-2 py-1 rounded bg-amber-100 text-stone-700 font-mono">origin:{origin}</span> : null}
              {fidelity ? <span className="px-2 py-1 rounded bg-emerald-100 text-emerald-800 font-mono">fidelity:{fidelity}</span> : null}
            </div>
          </div>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={mergedRows} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#d6d3d1" />
                <XAxis
                  dataKey="x"
                  name={xLabelDisplay}
                  type={xIsNumeric ? "number" : "category"}
                  domain={xIsNumeric ? xDomain : undefined}
                  allowDataOverflow={xIsNumeric}
                  tick={{ fontSize: 11 }}
                  label={{ value: xLabelDisplay, position: "bottom", offset: 0, fontSize: 11 }}
                />
                <YAxis
                  dataKey="y"
                  type="number"
                  domain={yDomain}
                  allowDataOverflow
                  tick={{ fontSize: 11 }}
                  tickFormatter={(v) => formatYValue(Number(v), yFormat)}
                  label={{ value: yLabelDisplay, angle: -90, position: "insideLeft", fontSize: 11 }}
                />
                <Tooltip
                  formatter={(v: number, name: string) => [
                    formatYValue(v, yFormat),
                    name === "yFit" ? "Linear fit" : yLabelDisplay,
                  ]}
                  labelFormatter={(l) => `${xLabelDisplay}: ${l}`}
                />
                <Line type="monotone" dataKey="y" stroke="#15803d" strokeWidth={2} dot={{ r: 3 }} />
                {uploaded.length > 0 && (
                  <Line type="monotone" dataKey="yUploaded" stroke="#ea580c" strokeWidth={2} dot={{ r: 2 }} connectNulls={false} />
                )}
                {regression && (
                  <Line
                    type="linear"
                    dataKey="yFit"
                    stroke="#2563eb"
                    strokeWidth={2}
                    strokeDasharray="6 4"
                    dot={false}
                    connectNulls={false}
                  />
                )}
              </LineChart>
            </ResponsiveContainer>
          </div>
          <p className="text-xs text-stone-500 mt-2">
            Data-driven labels/units from series payload (`x_label`, `y_label`, `x_unit`, `y_unit`, `y_format`) with automatic fallback.
          </p>
          <p className="text-xs text-stone-500 mt-1">
            This chart is an evidence-conditioned simulation for planning support, not a literal reproduction of any single paper protocol.
          </p>

          {regression && (
            <div className="mt-3 rounded border border-amber-200 bg-white/80 p-3 text-xs text-stone-700">
              <div className="font-medium mb-1">Quick linear regression (exploratory)</div>
              <div className="font-mono">n={regression.n} | slope={regression.slope.toExponential(3)} | intercept={regression.intercept.toExponential(3)} | R²={regression.r2.toFixed(4)}</div>
              <div className="mt-1 text-stone-500">
                Exploratory only: linear fit can be misleading for nonlinear surfaces or non-independent samples.
              </div>
            </div>
          )}
          <div className="mt-3 rounded border border-amber-200 bg-white/80 p-3">
            <div className="text-xs text-stone-600 mb-2">Upload measured CSV (first column = x, second numeric column = y)</div>
            <input
              type="file"
              accept=".csv,text/csv"
              onChange={async (e) => {
                const file = e.currentTarget.files?.[0];
                if (!file) return;
                const text = await file.text();
                setUploaded(parseCsvPairs(text));
              }}
              className="text-xs"
            />
            {uploaded.length > 0 && (
              <div className="mt-2 text-xs text-stone-700">
                Uploaded points: {uploaded.length}
                {mae != null ? ` · MAE vs simulated: ${formatYValue(mae, yFormat)}` : " · No overlapping x-values for MAE"}
              </div>
            )}
          </div>
        </div>
      )}

      <ProcedureTracePanel trace={procedureTrace} />

      <ObservationsTablePanel observations={observations} />

      <ArtifactJsonPanel
        artifact={artifact}
        emptyMessage="Interpretation is produced after the interpret stage completes."
        title="Interpretation (from run)"
      />
    </div>
  );
}
