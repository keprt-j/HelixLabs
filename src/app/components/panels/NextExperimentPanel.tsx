import { TrendingUp } from "lucide-react";
import { ArtifactJsonPanel } from "./ArtifactJsonPanel";

interface NextExperimentPanelProps {
  recommendation?: Record<string, unknown> | null;
}

export function NextExperimentPanel({ recommendation }: NextExperimentPanelProps) {
  const text = typeof recommendation?.recommendation === "string" ? recommendation.recommendation : "";
  const eig =
    typeof recommendation?.expected_information_gain === "number"
      ? recommendation.expected_information_gain
      : null;
  const risk = typeof recommendation?.risk_level === "number" ? recommendation.risk_level : null;

  if (!recommendation || Object.keys(recommendation).length === 0) {
    return (
      <ArtifactJsonPanel
        artifact={null}
        emptyMessage="Next-experiment recommendation is generated near the end of the outcomes pipeline (recommend-next stage)."
      />
    );
  }

  return (
    <div className="space-y-4">
      <div className="bg-blue-100/40 border border-blue-700 rounded-lg p-6">
        <div className="flex items-start gap-3 mb-4">
          <TrendingUp className="w-6 h-6 text-blue-700 flex-shrink-0" />
          <div>
            <h3 className="text-lg text-blue-800 mb-2">Recommended next experiment</h3>
            <p className="text-stone-900">{text || "—"}</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="p-4 bg-yellow-50/50 rounded border border-amber-200/80">
            <div className="text-xs text-stone-600 mb-1 font-mono">EXPECTED INFORMATION GAIN</div>
            <div className="text-2xl text-stone-900">{eig != null ? eig.toFixed(2) : "—"}</div>
          </div>
          <div className="p-4 bg-yellow-50/50 rounded border border-amber-200/80">
            <div className="text-xs text-stone-600 mb-1 font-mono">RISK LEVEL</div>
            <div className="text-2xl text-stone-900">{risk != null ? risk.toFixed(2) : "—"}</div>
          </div>
        </div>

        <div className="mt-4">
          <div className="text-xs text-stone-600 mb-2 font-mono">RAW PAYLOAD</div>
          <pre className="text-xs text-stone-800 bg-white/70 border border-amber-200 rounded-lg p-4 overflow-x-auto max-h-64">
            {JSON.stringify(recommendation, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  );
}
