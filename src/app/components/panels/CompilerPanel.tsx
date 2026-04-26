import { AlertTriangle } from "lucide-react";

interface CompilerPanelProps {
  experimentIr?: Record<string, unknown> | null;
  feasibilityReport?: Record<string, unknown> | null;
  valueScore?: Record<string, unknown> | null;
  protocol?: Record<string, unknown> | null;
}

function JsonBlock({ label, data }: { label: string; data: Record<string, unknown> | null | undefined }) {
  if (!data || Object.keys(data).length === 0) return null;
  return (
    <div>
      <div className="text-xs text-stone-600 mb-2 font-mono">{label}</div>
      <pre className="text-xs text-stone-800 bg-amber-50/80 border border-amber-200 rounded p-3 overflow-x-auto max-h-64">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
}

export function CompilerPanel({ experimentIr, feasibilityReport, valueScore, protocol }: CompilerPanelProps) {
  const hasAny =
    (experimentIr && Object.keys(experimentIr).length > 0) ||
    (feasibilityReport && Object.keys(feasibilityReport).length > 0) ||
    (valueScore && Object.keys(valueScore).length > 0) ||
    (protocol && Object.keys(protocol).length > 0);

  const issues = Array.isArray(feasibilityReport?.issues) ? (feasibilityReport!.issues as unknown[]) : [];
  const status = typeof feasibilityReport?.validation_status === "string" ? feasibilityReport.validation_status : "";

  if (!hasAny) {
    return (
      <div className="rounded-lg border border-amber-200 bg-yellow-50/50 p-6 text-sm text-stone-600">
        Planning artifacts (IR, feasibility, value, protocol) show here after you advance past the claim-graph stage.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="bg-yellow-50/50 border border-amber-200 rounded-lg p-6 space-y-6">
        <h3 className="text-sm text-stone-600 mb-2">Experiment compiler & planning</h3>
        <JsonBlock label="EXPERIMENT_IR" data={experimentIr ?? undefined} />
        <JsonBlock label="FEASIBILITY_REPORT" data={feasibilityReport ?? undefined} />
        <JsonBlock label="VALUE_SCORE" data={valueScore ?? undefined} />
        <JsonBlock label="PROTOCOL" data={protocol ?? undefined} />
      </div>

      {issues.length > 0 && (
        <div className="bg-yellow-100/50 border border-yellow-700 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-yellow-700 mt-0.5 flex-shrink-0" />
            <div>
              <div className="text-sm text-yellow-800 mb-2">
                Feasibility {status ? `(${status})` : ""}
              </div>
              <ul className="text-sm text-stone-700 list-disc pl-4 space-y-1">
                {issues.map((x, i) => (
                  <li key={i}>{typeof x === "string" ? x : JSON.stringify(x)}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
