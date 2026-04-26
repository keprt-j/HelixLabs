import { ArrowDown } from "lucide-react";

interface ClaimGraphPanelProps {
  claimGraph?: Record<string, unknown> | null;
}

export function ClaimGraphPanel({ claimGraph }: ClaimGraphPanelProps) {
  const main = typeof claimGraph?.main_claim === "string" ? claimGraph.main_claim : "";
  const weakest = typeof claimGraph?.weakest_claim === "string" ? claimGraph.weakest_claim : "";
  const nextTarget = typeof claimGraph?.next_target === "string" ? claimGraph.next_target : "";
  const ctx = claimGraph?.context && typeof claimGraph.context === "object" ? (claimGraph.context as Record<string, unknown>) : null;

  if (!claimGraph || Object.keys(claimGraph).length === 0) {
    return (
      <div className="rounded-lg border border-amber-200 bg-yellow-50/50 p-6 text-sm text-stone-600">
        Claim graph is produced after prior-work and negative-results checks. Advance the run if you are still on earlier
        stages.
      </div>
    );
  }

  return (
    <div className="bg-yellow-50/50 border border-amber-200 rounded-lg p-6">
      <h3 className="text-sm text-stone-600 mb-6">Hypothesis focus</h3>

      <div className="space-y-4">
        <div className="border border-green-700 bg-green-100/40 rounded-lg p-4">
          <div className="flex items-start justify-between mb-2 gap-2">
            <div className="text-stone-900">{main || "—"}</div>
            <div className="px-2 py-0.5 bg-green-700 text-green-100 text-xs rounded shrink-0">Main claim</div>
          </div>
          <div className="text-xs text-stone-600 font-mono">MAIN CLAIM</div>
        </div>

        <div className="flex justify-center">
          <ArrowDown className="w-4 h-4 text-stone-600" />
        </div>

        <div className="ml-0 md:ml-8 space-y-3">
          <div className="border border-amber-300 bg-amber-50/50 rounded-lg p-4">
            <div className="flex items-start justify-between mb-2 gap-2">
              <div className="text-stone-900 text-sm">{weakest || "—"}</div>
              <div className="px-2 py-0.5 bg-amber-700 text-amber-100 text-xs rounded shrink-0">Weakest</div>
            </div>
            <div className="text-xs text-stone-600 font-mono">WEAKEST CLAIM</div>
          </div>
        </div>

        {ctx && (ctx.novelty_score != null || ctx.redundancy_score != null) && (
          <div className="text-xs text-stone-600 font-mono flex gap-4 flex-wrap">
            {ctx.novelty_score != null && <span>novelty: {String(ctx.novelty_score)}</span>}
            {ctx.redundancy_score != null && <span>redundancy: {String(ctx.redundancy_score)}</span>}
          </div>
        )}

        <div className="mt-6 p-4 bg-yellow-100/50 border border-yellow-700 rounded">
          <div className="text-xs text-yellow-800 mb-1 font-mono">NEXT TARGET</div>
          <div className="text-stone-900 text-sm">{nextTarget || "—"}</div>
        </div>
      </div>
    </div>
  );
}
