import React from "react";
import { ArrowDown } from "lucide-react";

interface ClaimGraphPanelProps {
  claimGraph?: Record<string, unknown> | null;
  onSelectHypothesis?: (hypothesisId: string) => void | Promise<void>;
  busy?: boolean;
}

export function ClaimGraphPanel({ claimGraph, onSelectHypothesis, busy }: ClaimGraphPanelProps) {
  const main = cleanClaim(
    typeof claimGraph?.display_main_claim === "string"
      ? claimGraph.display_main_claim
      : typeof claimGraph?.main_claim === "string"
        ? claimGraph.main_claim
        : "",
  );
  const weakest = cleanClaim(
    typeof claimGraph?.display_weakest_claim === "string"
      ? claimGraph.display_weakest_claim
      : typeof claimGraph?.weakest_claim === "string"
        ? claimGraph.weakest_claim
        : "",
  );
  const nextTarget = cleanClaim(
    typeof claimGraph?.display_next_target === "string"
      ? claimGraph.display_next_target
      : typeof claimGraph?.next_target === "string"
        ? claimGraph.next_target
        : "",
  );
  const selectedId = typeof claimGraph?.selected_hypothesis_id === "string" ? claimGraph.selected_hypothesis_id : null;
  const selectedReason =
    typeof claimGraph?.selected_hypothesis_reason === "string" ? claimGraph.selected_hypothesis_reason : null;
  const hypothesesRaw = Array.isArray(claimGraph?.hypotheses) ? claimGraph?.hypotheses : [];
  const hypotheses = hypothesesRaw
    .map((h) => (h && typeof h === "object" ? (h as Record<string, unknown>) : null))
    .filter((h): h is Record<string, unknown> => h !== null);
  const displayHypothesesRaw = Array.isArray(claimGraph?.display_hypotheses) ? claimGraph?.display_hypotheses : [];
  const displayById = new Map(
    displayHypothesesRaw
      .map((h) => (h && typeof h === "object" ? (h as Record<string, unknown>) : null))
      .filter((h): h is Record<string, unknown> => h !== null)
      .map((h) => [String(h.id ?? ""), h]),
  );
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

        <div className="mt-6 space-y-3">
          <div className="text-xs text-stone-600 font-mono">HYPOTHESIS SHORTLIST (3)</div>
          {hypotheses.length > 0 ? (
            hypotheses.map((h) => {
              const id = typeof h.id === "string" ? h.id : "H?";
              const display = displayById.get(id);
              const title = cleanClaim(
                typeof display?.title === "string"
                  ? display.title
                  : typeof h.title === "string"
                    ? h.title
                    : "Hypothesis",
              );
              const statement = cleanClaim(
                typeof display?.statement === "string"
                  ? display.statement
                  : typeof h.statement === "string"
                    ? h.statement
                    : "—",
              );
              const rationale = cleanClaim(typeof display?.rationale === "string" ? display.rationale : "");
              const score = typeof h.score === "number" ? h.score : null;
              const active = selectedId != null && id === selectedId;
              return (
                <div
                  key={id}
                  className={`rounded-lg border p-3 ${active ? "border-green-700 bg-green-100/40" : "border-amber-200 bg-white/70"}`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="text-sm text-stone-900">
                      <span className="font-mono mr-2">{id}</span>
                      {title}
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      {score != null && <span className="text-xs font-mono text-stone-600">score={score.toFixed(2)}</span>}
                      {active && <span className="text-xs px-2 py-0.5 rounded bg-green-700 text-green-100">Selected</span>}
                      {!active && onSelectHypothesis && (
                        <button
                          onClick={() => onSelectHypothesis(id)}
                          disabled={Boolean(busy)}
                          className="text-xs px-2 py-0.5 rounded bg-stone-800 text-stone-100 hover:bg-stone-700 disabled:opacity-50"
                        >
                          {busy ? "Selecting..." : "Select"}
                        </button>
                      )}
                    </div>
                  </div>
                  <div className="text-sm text-stone-800 mt-1">{statement}</div>
                  {rationale && <div className="text-xs text-stone-600 mt-2">{rationale}</div>}
                </div>
              );
            })
          ) : (
            <div className="text-sm text-stone-600">No shortlist available.</div>
          )}
          {selectedReason && <div className="text-xs text-stone-600">{selectedReason}</div>}
        </div>
      </div>
    </div>
  );
}

function cleanClaim(value: string): string {
  if (typeof document === "undefined") {
    return (value || "")
      .replace(/&lt;/g, "<")
      .replace(/&gt;/g, ">")
      .replace(/&amp;/g, "&")
      .replace(/<\s*sub\s*>(.*?)<\s*\/\s*sub\s*>/gi, "$1")
      .replace(/<[^>]+>/g, "")
      .replace(/\s+/g, " ")
      .trim();
  }
  const element = document.createElement("textarea");
  element.innerHTML = value || "";
  return element.value
    .replace(/<\s*sub\s*>(.*?)<\s*\/\s*sub\s*>/gi, "$1")
    .replace(/<[^>]+>/g, "")
    .replace(/\s+/g, " ")
    .trim();
}
