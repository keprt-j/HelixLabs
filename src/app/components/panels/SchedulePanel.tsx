interface SchedulePanelProps {
  schedule?: Record<string, unknown> | null;
  protocol?: Record<string, unknown> | null;
}

export function SchedulePanel({ schedule, protocol }: SchedulePanelProps) {
  const sid = typeof schedule?.schedule_id === "string" ? schedule.schedule_id : "";
  const hours = typeof schedule?.total_duration_hours === "number" ? schedule.total_duration_hours : null;
  const util = typeof schedule?.resource_utilization_pct === "number" ? schedule.resource_utilization_pct : null;
  const idle = typeof schedule?.idle_time_hours === "number" ? schedule.idle_time_hours : null;
  const steps = Array.isArray(protocol?.steps) ? (protocol!.steps as unknown[]).map((s) => String(s)) : [];

  if (!schedule || Object.keys(schedule).length === 0) {
    return (
      <div className="rounded-lg border border-amber-200 bg-yellow-50/50 p-6 text-sm text-stone-600">
        Schedule metrics are generated at the end of planning (after protocol). Use <span className="font-medium">Advance</span>{" "}
        from the header until the workflow reaches approval.
      </div>
    );
  }

  return (
    <div className="bg-yellow-50/50 border border-amber-200 rounded-lg p-6 space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <h3 className="text-sm text-stone-600">Resource schedule</h3>
        {sid ? <div className="text-xs font-mono text-stone-500">{sid}</div> : null}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 bg-amber-50/50 rounded border border-amber-200/80">
          <div className="text-xs text-stone-600 mb-1 font-mono">TOTAL DURATION</div>
          <div className="text-2xl text-stone-900">{hours != null ? `${hours} h` : "—"}</div>
        </div>
        <div className="p-4 bg-amber-50/50 rounded border border-amber-200/80">
          <div className="text-xs text-stone-600 mb-1 font-mono">RESOURCE UTILIZATION</div>
          <div className="text-2xl text-stone-900">{util != null ? `${util}%` : "—"}</div>
        </div>
        <div className="p-4 bg-amber-50/50 rounded border border-amber-200/80">
          <div className="text-xs text-stone-600 mb-1 font-mono">IDLE TIME</div>
          <div className="text-2xl text-stone-900">{idle != null ? `${idle} h` : "—"}</div>
        </div>
      </div>

      {steps.length > 0 && (
        <div>
          <div className="text-xs text-stone-600 mb-2 font-mono">PROTOCOL STEPS</div>
          <ol className="list-decimal pl-5 space-y-1 text-sm text-stone-800">
            {steps.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ol>
        </div>
      )}

      <pre className="text-xs text-stone-700 bg-white/60 border border-amber-200 rounded p-3 overflow-x-auto">
        {JSON.stringify(schedule, null, 2)}
      </pre>
    </div>
  );
}
