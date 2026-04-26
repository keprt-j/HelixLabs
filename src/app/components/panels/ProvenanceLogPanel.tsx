import { Circle } from "lucide-react";

export type ProvenanceEventRow = {
  time: string;
  event_type: string;
  category: string;
  message: string;
};

function colorForEventType(t: string): string {
  const m: Record<string, string> = {
    STATE: "text-blue-600",
    DECISION: "text-purple-600",
    MODEL: "text-green-600",
    ERROR: "text-red-600",
    FIX: "text-yellow-600",
  };
  return m[t] ?? "text-stone-600";
}

interface ProvenanceLogPanelProps {
  events?: ProvenanceEventRow[] | null;
}

export function ProvenanceLogPanel({ events }: ProvenanceLogPanelProps) {
  const list = Array.isArray(events) ? events : [];

  if (list.length === 0) {
    return (
      <div className="rounded-lg border border-amber-200 bg-yellow-50/50 p-6 text-sm text-stone-600">
        Provenance events will appear as you advance the run. Create a run from the home page if you have not yet.
      </div>
    );
  }

  return (
    <div className="bg-yellow-50/50 border border-amber-200 rounded-lg p-6">
      <div className="flex items-center justify-between mb-6 flex-wrap gap-2">
        <h3 className="text-sm text-stone-600">Event timeline</h3>
        <div className="flex items-center gap-4 text-xs flex-wrap">
          {["STATE", "DECISION", "MODEL", "ERROR", "FIX"].map((t) => (
            <div key={t} className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${colorForEventType(t).replace("text-", "bg-")}`} />
              <span className="text-stone-600">{t}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="space-y-0 relative">
        <div className="absolute left-3 top-0 bottom-0 w-px bg-amber-300" />

        {list.map((event, idx) => {
          const color = colorForEventType(event.event_type);
          return (
            <div key={`${event.time}-${idx}`} className="relative flex items-start gap-4 pb-6">
              <div className="relative z-10">
                <Circle className={`w-6 h-6 ${color} fill-current`} />
              </div>

              <div className="flex-1 pt-0.5 min-w-0">
                <div className="flex items-start justify-between mb-1 gap-2 flex-wrap">
                  <div className="flex items-center gap-3 flex-wrap">
                    <span className="text-xs font-mono text-stone-600">{event.time}</span>
                    <span className={`text-xs px-2 py-0.5 rounded ${color} bg-opacity-20`}>{event.event_type}</span>
                  </div>
                  <span className="text-xs text-stone-600">{event.category}</span>
                </div>

                <div className="text-sm text-stone-900 break-words">{event.message}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
