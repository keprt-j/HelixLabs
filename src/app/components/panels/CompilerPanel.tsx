import { AlertTriangle } from "lucide-react";
import { PipelineJsonInspector } from "./PipelineJsonInspector";

interface CompilerPanelProps {
  experimentIr?: Record<string, unknown> | null;
  feasibilityReport?: Record<string, unknown> | null;
  protocol?: Record<string, unknown> | null;
  artifactSummaries?: Record<string, unknown> | null;
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

function JsonBlock({
  artifactSummaries,
  data,
  label,
  summaryKey,
}: {
  artifactSummaries?: Record<string, unknown> | null;
  data: Record<string, unknown> | null | undefined;
  label: string;
  summaryKey: string;
}) {
  if (!data || Object.keys(data).length === 0) return null;
  const meta = summaryFor(artifactSummaries, summaryKey);
  return (
    <PipelineJsonInspector
      title={label}
      summary={meta.summary}
      generatedAt={meta.generatedAt}
      data={data}
    />
  );
}

export function CompilerPanel({
  artifactSummaries,
  experimentIr,
  feasibilityReport,
  protocol,
}: CompilerPanelProps) {
  const hasAny =
    (experimentIr && Object.keys(experimentIr).length > 0) ||
    (feasibilityReport && Object.keys(feasibilityReport).length > 0) ||
    (protocol && Object.keys(protocol).length > 0);

  const issues = Array.isArray(feasibilityReport?.issues) ? (feasibilityReport!.issues as unknown[]) : [];
  const status = typeof feasibilityReport?.validation_status === "string" ? feasibilityReport.validation_status : "";

  if (!hasAny) {
    return (
      <div className="rounded-lg border border-amber-200 bg-yellow-50/50 p-6 text-sm text-stone-600">
        Planning artifacts (IR, feasibility, protocol) show here after you advance past the claim-graph stage.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="bg-yellow-50/50 border border-amber-200 rounded-lg p-6 space-y-6">
        <h3 className="text-sm text-stone-600 mb-2">Experiment compiler & planning</h3>
        <JsonBlock label="EXPERIMENT_IR" summaryKey="experiment_ir" data={experimentIr ?? undefined} artifactSummaries={artifactSummaries} />
        <JsonBlock label="FEASIBILITY_REPORT" summaryKey="feasibility_report" data={feasibilityReport ?? undefined} artifactSummaries={artifactSummaries} />
        <JsonBlock label="PROTOCOL" summaryKey="protocol" data={protocol ?? undefined} artifactSummaries={artifactSummaries} />
      </div>

      {issues.length > 0 && (
        <div className="bg-yellow-100/50 border border-yellow-700 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-yellow-700 mt-0.5 flex-shrink-0" />
            <div>
              <div className="text-sm text-yellow-800 mb-2">
                Feasibility {status ? `(${status})` : ""}
              </div>
              <ul className="text-sm text-stone-700 list-disc pl-4 space-y-1">
                {issues.map((x, i) => (
                  <li key={i}>{typeof x === "string" ? x : JSON.stringify(x)}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
