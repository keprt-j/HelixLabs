import { AlertCircle, CheckCircle2 } from "lucide-react";
import { PipelineJsonInspector } from "./PipelineJsonInspector";

function asStringList(v: unknown): string[] {
  if (!Array.isArray(v)) return [];
  return v.map((x) => (typeof x === "string" ? x : String(x))).filter(Boolean);
}

interface PriorWorkPanelProps {
  artifactSummaries?: Record<string, unknown> | null;
  priorWork?: Record<string, unknown> | null;
  negativeResults?: Record<string, unknown> | null;
  valueScore?: Record<string, unknown> | null;
}

function summaryFor(artifactSummaries: Record<string, unknown> | null | undefined, key: string) {
  const value = artifactSummaries?.[key];
  if (!value || typeof value !== "object") return { summary: null, generatedAt: null };
  const record = value as Record<string, unknown>;
  return {
    summary: typeof record.summary === "string" ? record.summary : null,
    generatedAt: typeof record.generated_at === "string" ? record.generated_at : null,
  };
}

export function PriorWorkPanel({ artifactSummaries, priorWork, negativeResults, valueScore }: PriorWorkPanelProps) {
  const novelty = typeof priorWork?.novelty_score === "number" ? priorWork.novelty_score : null;
  const redundancy = typeof priorWork?.redundancy_score === "number" ? priorWork.redundancy_score : null;
  const knownRuns = asStringList(priorWork?.known_runs);
  const gap = typeof priorWork?.gap === "string" ? priorWork.gap : "";
  const neg = Array.isArray(negativeResults?.negative_results) ? negativeResults!.negative_results : [];
  const valueScoreSummary = summaryFor(artifactSummaries, "value_score");

  const hasPrior = priorWork && Object.keys(priorWork).length > 0;

  if (!hasPrior) {
    return (
      <div className="rounded-lg border border-amber-200 bg-yellow-50/50 p-6 text-sm text-stone-600">
        Prior-work scoring will appear here after the literature stage completes on your run.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-green-100/30 border border-green-700 rounded-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle2 className="w-4 h-4 text-green-700" />
            <h3 className="text-sm text-green-800">Known prior coverage</h3>
          </div>
          <div className="space-y-2">
            {knownRuns.length === 0 ? (
              <div className="text-stone-600 text-sm">No labeled prior runs in this demo payload.</div>
            ) : (
              knownRuns.map((line) => (
                <div key={line} className="text-stone-700 text-sm">
                  <span className="font-mono text-stone-900">{line.split("—")[0]?.trim() || line}</span>
                  {line.includes("—") ? ` — ${line.split("—").slice(1).join("—").trim()}` : null}
                </div>
              ))
            )}
          </div>
        </div>

        <div className="bg-yellow-100/40 border border-yellow-700 rounded-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <AlertCircle className="w-4 h-4 text-yellow-700" />
            <h3 className="text-sm text-yellow-800">Gap & negative signals</h3>
          </div>
          <div className="space-y-2 text-sm text-stone-700">
            {gap ? <p>{gap}</p> : <p>No gap summary provided.</p>}
            {neg.length > 0 && (
              <ul className="mt-2 list-disc pl-4 space-y-1 text-stone-600">
                {neg.map((item: unknown, i: number) => {
                  const row = item as Record<string, unknown>;
                  const cond = typeof row.condition === "string" ? row.condition : "condition";
                  const ft = typeof row.failure_type === "string" ? row.failure_type : "";
                  return (
                    <li key={i}>
                      {cond}
                      {ft ? ` (${ft})` : ""}
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
        </div>
      </div>

      <div className="bg-yellow-50/50 border border-amber-200 rounded-lg p-6">
        <h3 className="text-sm text-stone-600 mb-4">Overlap analysis</h3>

        <div className="grid grid-cols-2 gap-6">
          <div>
            <div className="text-xs text-stone-600 mb-1 font-mono">NOVELTY SCORE</div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl text-green-700">{novelty != null ? novelty : "—"}</span>
              <span className="text-stone-600">/10</span>
            </div>
          </div>

          <div>
            <div className="text-xs text-stone-600 mb-1 font-mono">REDUNDANCY SCORE</div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl text-yellow-700">{redundancy != null ? redundancy : "—"}</span>
              <span className="text-stone-600">/10</span>
            </div>
          </div>
        </div>
      </div>

      {valueScore && Object.keys(valueScore).length > 0 ? (
        <PipelineJsonInspector
          title="VALUE_SCORE"
          summary={valueScoreSummary.summary}
          generatedAt={valueScoreSummary.generatedAt}
          data={valueScore}
        />
      ) : null}
    </div>
  );
}
