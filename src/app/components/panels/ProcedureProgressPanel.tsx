interface ProcedureProgressPanelProps {
  trace?: Array<Record<string, unknown>> | null;
}

export function ProcedureProgressPanel({ trace }: ProcedureProgressPanelProps) {
  const steps = Array.isArray(trace) ? trace : [];
  const latest = steps.length > 0 ? String(steps[steps.length - 1]?.status ?? "unknown") : "not_started";
  return (
    <div className="rounded-lg border border-emerald-200 bg-emerald-50/50 p-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm text-emerald-800">Procedure progress</h3>
        <span className="text-xs font-mono text-emerald-700">status:{latest}</span>
      </div>
      {steps.length === 0 ? (
        <div className="text-sm text-emerald-800">No procedure trace yet.</div>
      ) : (
        <div className="space-y-1">
          {steps.slice(0, 8).map((s, i) => (
            <div key={i} className="text-xs text-emerald-900 font-mono truncate">
              {String(s.id ?? `step_${i + 1}`)} · {String(s.name ?? "step")} · {String(s.status ?? "unknown")}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
