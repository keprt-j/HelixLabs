import { Circle } from "lucide-react";

export function ProvenanceLogPanel() {
  const events = [
    {
      time: "2026-04-25 09:00:12",
      type: "STATE",
      category: "Initialization",
      message: "Experiment RUN-4729 created from goal input",
      color: "text-blue-600",
    },
    {
      time: "2026-04-25 09:00:45",
      type: "DECISION",
      category: "Planning",
      message: "Compiler selected Fe-doped variant based on novelty score (7.2/10)",
      color: "text-purple-600",
    },
    {
      time: "2026-04-25 09:01:23",
      type: "MODEL",
      category: "Inference",
      message: "Predicted optimal Fe concentration: 3-5 mol% (confidence: 72%)",
      color: "text-green-600",
    },
    {
      time: "2026-04-25 09:02:18",
      type: "STATE",
      category: "Scheduling",
      message: "Resource allocation complete. Total duration: 28h, utilization: 67%",
      color: "text-blue-600",
    },
    {
      time: "2026-04-25 09:15:23",
      type: "STATE",
      category: "Execution",
      message: "Synthesis started: Batch 1/3",
      color: "text-blue-600",
    },
    {
      time: "2026-04-25 14:32:18",
      type: "ERROR",
      category: "Failure",
      message: "XRD analysis failed: insufficient peak intensity (142 counts, min 500)",
      color: "text-red-600",
    },
    {
      time: "2026-04-25 14:33:45",
      type: "DECISION",
      category: "Recovery",
      message: "Selected recovery: Retry step with sample re-polishing (+45 min)",
      color: "text-purple-600",
    },
    {
      time: "2026-04-25 14:35:02",
      type: "FIX",
      category: "Auto-repair",
      message: "Sample surface polished. XRD requeued.",
      color: "text-yellow-600",
    },
    {
      time: "2026-04-25 15:22:15",
      type: "STATE",
      category: "Execution",
      message: "XRD analysis complete. Phase purity: 97.2%",
      color: "text-blue-600",
    },
    {
      time: "2026-04-25 16:45:32",
      type: "FIX",
      category: "Data validation",
      message: "Auto-mapped column: temp_celsius → temperature",
      color: "text-yellow-600",
    },
    {
      time: "2026-04-25 16:45:33",
      type: "FIX",
      category: "Data validation",
      message: "Auto-mapped column: sigma_ionic → conductivity",
      color: "text-yellow-600",
    },
    {
      time: "2026-04-25 16:45:34",
      type: "FIX",
      category: "Data validation",
      message: "Auto-mapped column: e_hull → activation_energy",
      color: "text-yellow-600",
    },
    {
      time: "2026-04-25 16:46:12",
      type: "STATE",
      category: "Validation",
      message: "Data validation complete. 35 records validated.",
      color: "text-blue-600",
    },
    {
      time: "2026-04-25 16:50:28",
      type: "MODEL",
      category: "Inference",
      message: "Inferred: Fe²⁺ doping creates oxygen vacancies (confidence: 87%)",
      color: "text-green-600",
    },
    {
      time: "2026-04-25 16:51:05",
      type: "DECISION",
      category: "Next step",
      message: "Recommended next: Fine-grained concentration sweep (3-7 mol%)",
      color: "text-purple-600",
    },
    {
      time: "2026-04-25 16:52:00",
      type: "STATE",
      category: "Completion",
      message: "Experiment RUN-4729 completed successfully",
      color: "text-blue-600",
    },
  ];

  return (
    <div className="bg-yellow-50/50 border border-amber-200 rounded-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-sm text-stone-600">Event Timeline</h3>
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-blue-600 rounded-full" />
            <span className="text-stone-600">State</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-purple-600 rounded-full" />
            <span className="text-stone-600">Decision</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-600 rounded-full" />
            <span className="text-stone-600">Model</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-yellow-600 rounded-full" />
            <span className="text-stone-600">Fix</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-red-600 rounded-full" />
            <span className="text-stone-600">Error</span>
          </div>
        </div>
      </div>

      <div className="space-y-0 relative">
        <div className="absolute left-3 top-0 bottom-0 w-px bg-amber-300" />

        {events.map((event, idx) => (
          <div key={idx} className="relative flex items-start gap-4 pb-6">
            <div className="relative z-10">
              <Circle className={`w-6 h-6 ${event.color} fill-current`} />
            </div>

            <div className="flex-1 pt-0.5">
              <div className="flex items-start justify-between mb-1">
                <div className="flex items-center gap-3">
                  <span className="text-xs font-mono text-stone-600">{event.time}</span>
                  <span className={`text-xs px-2 py-0.5 rounded ${event.color} bg-opacity-20`}>
                    {event.type}
                  </span>
                </div>
                <span className="text-xs text-stone-600">{event.category}</span>
              </div>

              <div className="text-sm text-stone-900">{event.message}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
