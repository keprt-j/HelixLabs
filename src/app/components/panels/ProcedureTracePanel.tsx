interface ProcedureTracePanelProps {
  trace?: Array<Record<string, unknown>> | null;
}

export function ProcedureTracePanel({ trace }: ProcedureTracePanelProps) {
  const steps = Array.isArray(trace) ? trace : [];
  if (steps.length === 0) {
    return (
      <div className="rounded-lg border border-amber-200 bg-yellow-50/50 p-4 text-sm text-stone-600">
        Procedure trace will appear after execution stages emit normalized artifacts.
      </div>
    );
  }

  return (
    <div className="bg-yellow-50/50 border border-amber-200 rounded-lg p-4">
      <h3 className="text-sm text-stone-600 mb-3">Procedure trace</h3>
      <div className="space-y-2">
        {steps.map((step, idx) => {
          const id = String(step.id ?? `step_${idx + 1}`);
          const name = String(step.name ?? "Unnamed step");
          const status = String(step.status ?? "unknown");
          return (
            <div key={`${id}-${idx}`} className="flex items-center justify-between gap-3 rounded border border-amber-200 bg-white/70 px-3 py-2">
              <div className="min-w-0">
                <div className="text-sm text-stone-900 truncate">{name}</div>
                <div className="text-xs text-stone-500 font-mono">{id}</div>
              </div>
              <div className="text-xs px-2 py-1 rounded bg-amber-100 text-stone-700 font-mono">{status}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
