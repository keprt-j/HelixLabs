import { CheckCircle2, Circle, Loader2 } from "lucide-react";

export function ExecutionPanel() {
  const steps = [
    { id: 1, name: "Initialize workspace", status: "complete", timestamp: "2026-04-25 09:15:23" },
    { id: 2, name: "Load precursors", status: "complete", timestamp: "2026-04-25 09:16:45" },
    { id: 3, name: "Mix powder (Fe₂O₃)", status: "complete", timestamp: "2026-04-25 09:18:12" },
    { id: 4, name: "Ball mill (300 rpm, 2h)", status: "complete", timestamp: "2026-04-25 09:20:00" },
    { id: 5, name: "Press pellets (100 MPa)", status: "running", timestamp: "2026-04-25 11:22:34" },
    { id: 6, name: "Sintering (1100°C, 6h)", status: "pending", timestamp: null },
    { id: 7, name: "Cool to RT", status: "pending", timestamp: null },
    { id: 8, name: "XRD characterization", status: "pending", timestamp: null },
    { id: 9, name: "Impedance measurement", status: "pending", timestamp: null },
  ];

  return (
    <div className="space-y-4">
      <div className="bg-yellow-50/50 border border-amber-200 rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm text-stone-600">Execution Progress</h3>
          <div className="text-sm text-stone-600">
            Step 5 of 9
          </div>
        </div>

        <div className="space-y-2">
          {steps.map((step) => {
            const Icon = step.status === "complete" ? CheckCircle2 : step.status === "running" ? Loader2 : Circle;
            const textColor = step.status === "complete" ? "text-green-600" : step.status === "running" ? "text-blue-600" : "text-stone-600";
            const bgColor = step.status === "running" ? "bg-blue-100/40 border-blue-700" : "bg-amber-50/50 border-amber-200";

            return (
              <div
                key={step.id}
                className={`flex items-center gap-3 p-3 rounded border ${bgColor}`}
              >
                <Icon className={`w-4 h-4 ${textColor} ${step.status === "running" ? "animate-spin" : ""}`} />
                <div className="flex-1">
                  <div className={`text-sm ${step.status === "pending" ? "text-stone-600" : "text-stone-900"}`}>
                    {step.name}
                  </div>
                  {step.timestamp && (
                    <div className="text-xs text-stone-600 font-mono mt-0.5">
                      {step.timestamp}
                    </div>
                  )}
                </div>
                {step.status === "complete" && (
                  <div className="text-xs text-green-600">✓</div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      <div className="bg-yellow-50/50 border border-amber-200 rounded-lg p-6">
        <h3 className="text-sm text-stone-600 mb-4">Instrument Logs</h3>

        <div className="bg-stone-900 rounded p-4 font-mono text-xs space-y-1 max-h-64 overflow-y-auto">
          <div className="text-stone-400">[09:15:23] INFO: Experiment RUN-4729 initialized</div>
          <div className="text-stone-400">[09:16:45] INFO: Precursor loaded: Li₂CO₃ (15.2g)</div>
          <div className="text-stone-400">[09:16:52] INFO: Precursor loaded: La₂O₃ (42.8g)</div>
          <div className="text-stone-400">[09:17:01] INFO: Precursor loaded: ZrO₂ (18.1g)</div>
          <div className="text-stone-400">[09:18:12] INFO: Dopant added: Fe₂O₃ (0.8g, 5 mol%)</div>
          <div className="text-stone-400">[09:20:00] INFO: Ball milling started</div>
          <div className="text-stone-400">[09:20:00] INSTRUMENT: Motor RPM = 300</div>
          <div className="text-stone-400">[11:20:02] INFO: Ball milling complete</div>
          <div className="text-stone-400">[11:22:34] INFO: Pellet pressing started</div>
          <div className="text-blue-400">[11:22:34] INSTRUMENT: Hydraulic press pressure = 100 MPa</div>
          <div className="text-blue-400">[11:22:35] INSTRUMENT: Sample diameter = 13.02 mm</div>
          <div className="text-blue-400">[11:22:35] STATUS: Running (pellet 1/5)</div>
        </div>
      </div>
    </div>
  );
}
