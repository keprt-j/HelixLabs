import { useCallback, useEffect, useState } from "react";
import {
  advanceRun,
  approveRun,
  createRun,
  fetchRun,
  replanRun,
  selectHypothesis,
  setRunSimulationOverrides,
} from "./api/runApi";
import { Header } from "./components/Header";
import { Sidebar } from "./components/Sidebar";
import { Homepage } from "./components/Homepage";
import { LiteratureReview } from "./components/LiteratureReview";
import { ResearchGoalPanel } from "./components/panels/ResearchGoalPanel";
import { PriorWorkPanel } from "./components/panels/PriorWorkPanel";
import { ClaimGraphPanel } from "./components/panels/ClaimGraphPanel";
import { CompilerPanel } from "./components/panels/CompilerPanel";
import { SchedulePanel } from "./components/panels/SchedulePanel";
import { ExecutionPanel } from "./components/panels/ExecutionPanel";
import { FailureRecoveryPanel } from "./components/panels/FailureRecoveryPanel";
import { DataValidationPanel } from "./components/panels/DataValidationPanel";
import { ResultsPanel } from "./components/panels/ResultsPanel";
import { NextExperimentPanel } from "./components/panels/NextExperimentPanel";
import { ProvenanceLogPanel } from "./components/panels/ProvenanceLogPanel";
import { RunSummaryPanel } from "./components/panels/RunSummaryPanel";
import { CompareRunsPanel } from "./components/panels/CompareRunsPanel";
import { ExperimentBriefPanel } from "./components/panels/ExperimentBriefPanel";
import { StageNarrativeBanner } from "./components/panels/StageNarrativeBanner";
import { ProcedureProgressPanel } from "./components/panels/ProcedureProgressPanel";
import { SimulationControlsPanel } from "./components/panels/SimulationControlsPanel";
import { PipelineJsonInspector } from "./components/panels/PipelineJsonInspector";
import { mapRunStateToHeaderStatus } from "./lib/runUi";
import type { HelixRun } from "./types/run";

const RUN_SESSION_KEY = "helixlabs_active_run_id";

function readStoredRunId(): string | null {
  try {
    const v = sessionStorage.getItem(RUN_SESSION_KEY);
    return v?.trim() ? v.trim() : null;
  } catch {
    return null;
  }
}

function persistRunId(id: string | null) {
  try {
    if (id) sessionStorage.setItem(RUN_SESSION_KEY, id);
    else sessionStorage.removeItem(RUN_SESSION_KEY);
  } catch {
    /* ignore */
  }
}

function asRecord(v: unknown): Record<string, unknown> | null {
  if (v && typeof v === "object" && !Array.isArray(v)) return v as Record<string, unknown>;
  return null;
}

type AppStage = "homepage" | "literature-review" | "dashboard";
type DashboardSection = "intake" | "planning" | "runtime" | "outcomes";
type IntakeTab = "goal" | "prior-work" | "claim-graph";
type PlanningTab = "compiler" | "simulation" | "schedule";
type RuntimeTab = "execution" | "recovery" | "validation" | "results";
type OutcomesTab = "summary" | "next" | "provenance" | "compare";
type SectionTabMap = {
  intake: IntakeTab;
  planning: PlanningTab;
  runtime: RuntimeTab;
  outcomes: OutcomesTab;
};
type ExportSubject = "hypothesis" | "experiment" | "results";
type ExportFormat = "json" | "pdf";

function linesFromValue(value: unknown, indent = 0): string[] {
  const pad = " ".repeat(indent);
  if (value == null) return [`${pad}-`];
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") return [`${pad}${String(value)}`];
  if (Array.isArray(value)) {
    if (value.length === 0) return [`${pad}(none)`];
    return value.flatMap((item) => {
      if (typeof item === "string" || typeof item === "number" || typeof item === "boolean") {
        return [`${pad}- ${String(item)}`];
      }
      return [`${pad}-`, ...linesFromValue(item, indent + 2)];
    });
  }
  const rec = asRecord(value);
  if (!rec) return [`${pad}${String(value)}`];
  const keys = Object.keys(rec);
  if (keys.length === 0) return [`${pad}(none)`];
  return keys.flatMap((key) => {
    const v = rec[key];
    if (v == null || typeof v === "string" || typeof v === "number" || typeof v === "boolean") {
      return [`${pad}${key}: ${String(v ?? "-")}`];
    }
    if (Array.isArray(v)) {
      const arrayLines = linesFromValue(v, indent + 2);
      return [`${pad}${key}:`, ...arrayLines];
    }
    return [`${pad}${key}:`, ...linesFromValue(v, indent + 2)];
  });
}

function downloadJson(payload: Record<string, unknown>, filename: string): void {
  const text = JSON.stringify(payload, null, 2);
  const blob = new Blob([text], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

async function downloadPdf(payload: Record<string, unknown>, title: string, filename: string): Promise<void> {
  const { jsPDF } = await import("jspdf");
  const doc = new jsPDF({ unit: "pt", format: "letter" });
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const margin = 42;
  let y = margin;
  doc.setFont("helvetica", "bold");
  doc.setFontSize(14);
  doc.text(title, margin, y);
  y += 20;
  doc.setFont("helvetica", "normal");
  doc.setFontSize(10);
  const lines = doc.splitTextToSize(linesFromValue(payload).join("\n"), pageWidth - margin * 2);
  for (const line of lines) {
    if (y > pageHeight - margin) {
      doc.addPage();
      y = margin;
    }
    doc.text(line, margin, y);
    y += 13;
  }
  doc.save(filename);
}

export default function App() {
  const [stage, setStage] = useState<AppStage>("homepage");
  const [experiment, setExperiment] = useState("");
  const [runId, setRunId] = useState<string | null>(() => readStoredRunId());
  const [run, setRun] = useState<HelixRun | null>(null);
  const [runError, setRunError] = useState<string | null>(null);
  const [actionBusy, setActionBusy] = useState(false);

  const [currentSection, setCurrentSection] = useState<DashboardSection>("intake");
  const [sectionTabs, setSectionTabs] = useState<SectionTabMap>({
    intake: "goal",
    planning: "compiler",
    runtime: "execution",
    outcomes: "summary",
  });

  const refreshRun = useCallback(async () => {
    if (!runId) return;
    setRunError(null);
    try {
      const r = await fetchRun(runId);
      setRun(r);
    } catch (e) {
      setRun(null);
      setRunError(e instanceof Error ? e.message : "Failed to load run");
    }
  }, [runId]);

  useEffect(() => {
    if (stage === "dashboard" && runId) {
      void refreshRun();
    }
  }, [stage, runId, refreshRun]);

  const handleAdvance = useCallback(async () => {
    if (!runId) return;
    setActionBusy(true);
    setRunError(null);
    try {
      const r = await advanceRun(runId);
      setRun(r);
    } catch (e) {
      setRunError(e instanceof Error ? e.message : "Advance failed");
    } finally {
      setActionBusy(false);
    }
  }, [runId]);

  const handleApprove = useCallback(async () => {
    if (!runId) return;
    setActionBusy(true);
    setRunError(null);
    try {
      const r = await approveRun(runId);
      setRun(r);
    } catch (e) {
      setRunError(e instanceof Error ? e.message : "Approve failed");
    } finally {
      setActionBusy(false);
    }
  }, [runId]);

  const handleExportSelection = useCallback(async (subject: ExportSubject, format: ExportFormat) => {
    if (!runId || !run) return;
    setActionBusy(true);
    setRunError(null);
    try {
      const base = {
        run_id: run.run_id,
        user_goal: run.user_goal,
        state: run.state,
        exported_at: new Date().toISOString(),
      };
      const claimGraph = asRecord(run.artifacts?.claim_graph) || {};
      const experimentBundle = asRecord(run.artifacts?.experiment_ir) || {};
      const experimentIr = asRecord(experimentBundle.experiment_ir) || {};
      const executionLog = asRecord(run.artifacts?.execution_log) || {};
      const normalizedResults = asRecord(run.artifacts?.normalized_results) || {};
      const report = asRecord(run.artifacts?.report) || {};
      let payload: Record<string, unknown>;
      if (subject === "hypothesis") {
        payload = {
          ...base,
          panel: "Claim Graph",
          main_claim: claimGraph.display_main_claim ?? claimGraph.main_claim ?? "",
          weakest_claim: claimGraph.display_weakest_claim ?? claimGraph.weakest_claim ?? "",
          next_target: claimGraph.display_next_target ?? claimGraph.next_target ?? "",
          selected_hypothesis_id: claimGraph.selected_hypothesis_id ?? null,
          selected_reason: claimGraph.selected_hypothesis_reason ?? null,
          hypotheses: Array.isArray(claimGraph.display_hypotheses)
            ? claimGraph.display_hypotheses
            : Array.isArray(claimGraph.hypotheses)
              ? claimGraph.hypotheses
              : [],
          context: asRecord(claimGraph.context) || {},
          literature_signals: {
            source: run.pipeline.intake?.literature?.source ?? null,
            evidence_manifest: run.pipeline.intake?.literature?.evidence_manifest ?? null,
            claim_evidence: run.pipeline.intake?.literature?.claim_evidence ?? null,
          },
        };
      } else if (subject === "experiment") {
        payload = {
          ...base,
          panel: "Experiment Compiler + Schedule",
          plugin: asRecord(experimentBundle.plugin) || {},
          target_claim: experimentBundle.target_claim ?? null,
          factors: Array.isArray(experimentIr.factors) ? experimentIr.factors : [],
          responses: Array.isArray(experimentIr.responses) ? experimentIr.responses : [],
          constraints: Array.isArray(experimentIr.constraints) ? experimentIr.constraints : [],
          design: asRecord(experimentIr.design) || {},
          procedure_steps: Array.isArray(experimentIr.procedure_steps) ? experimentIr.procedure_steps : [],
          analysis_plan: asRecord(experimentIr.analysis_plan) || {},
          design_matrix: Array.isArray(experimentBundle.design_matrix) ? experimentBundle.design_matrix : [],
          feasibility_report: asRecord(run.artifacts?.feasibility_report) || {},
          value_score: asRecord(run.artifacts?.value_score) || {},
          protocol: asRecord(run.artifacts?.protocol) || {},
          schedule: asRecord(run.artifacts?.schedule) || {},
          simulation_overrides: asRecord(run.artifacts?.simulation_overrides) || {},
        };
      } else {
        payload = {
          ...base,
          panel: "Results",
          interpretation_summary: asRecord(run.artifacts?.interpretation)?.inference ?? null,
          chart_series: Array.isArray(executionLog.series_for_charts) ? executionLog.series_for_charts : [],
          measurements: Array.isArray(executionLog.measurements) ? executionLog.measurements : [],
          procedure_trace: Array.isArray(normalizedResults.procedure_trace) ? normalizedResults.procedure_trace : [],
          observations: Array.isArray(normalizedResults.observations) ? normalizedResults.observations : [],
          validation_report: asRecord(run.artifacts?.validation_report) || {},
          interpretation: asRecord(run.artifacts?.interpretation) || {},
          normalized_results: normalizedResults,
          report,
        };
      }
      const baseName = `helixlabs-${subject}-${runId}`;
      if (format === "json") {
        downloadJson(payload, `${baseName}.json`);
      } else {
        await downloadPdf(payload, `HelixLabs ${subject} export`, `${baseName}.pdf`);
      }
    } catch (e) {
      setRunError(e instanceof Error ? e.message : "Export failed.");
    } finally {
      setActionBusy(false);
    }
  }, [runId, run]);

  const handleDemoWalkthrough = useCallback(async () => {
    if (!runId) return;
    setActionBusy(true);
    setRunError(null);
    try {
      let current = run ?? (await fetchRun(runId));
      for (let i = 0; i < 20; i++) {
        if (current.state === "MEMORY_UPDATED" || current.state === "REPORT_GENERATED") break;
        if (current.state === "AWAITING_HUMAN_APPROVAL") {
          current = await approveRun(runId);
        } else {
          current = await advanceRun(runId);
        }
        setRun(current);
      }
      setCurrentSection("outcomes");
      setSectionTabs((prev) => ({ ...prev, outcomes: "summary" }));
    } catch (e) {
      setRunError(e instanceof Error ? e.message : "Demo walkthrough failed");
    } finally {
      setActionBusy(false);
    }
  }, [runId, run]);

  const handleApplySimulationControls = useCallback(
    async (overrides: { n_replicates?: number; noise_scale_relative?: number; design_density?: "coarse" | "medium" | "fine" }) => {
      if (!runId) return;
      setActionBusy(true);
      setRunError(null);
      try {
        await setRunSimulationOverrides(runId, overrides);
        const replanned = await replanRun(runId);
        setRun(replanned);
      } catch (e) {
        setRunError(e instanceof Error ? e.message : "Failed to apply simulation controls");
      } finally {
        setActionBusy(false);
      }
    },
    [runId],
  );

  const handleSelectHypothesis = useCallback(
    async (hypothesisId: string) => {
      if (!runId || !run) return;
      setActionBusy(true);
      setRunError(null);
      try {
        let updated = await selectHypothesis(runId, hypothesisId);
        const replanEligible = new Set([
          "CLAIM_GRAPH_BUILT",
          "EXPERIMENT_IR_COMPILED",
          "FEASIBILITY_VALIDATED",
          "NOVELTY_VALUE_SCORED",
          "PROTOCOL_GENERATED",
          "AWAITING_HUMAN_APPROVAL",
        ]);
        if (replanEligible.has(updated.state)) {
          updated = await replanRun(runId);
        }
        setRun(updated);
      } catch (e) {
        setRunError(e instanceof Error ? e.message : "Failed to select hypothesis");
      } finally {
        setActionBusy(false);
      }
    },
    [runId, run],
  );

  if (stage === "homepage") {
    return (
      <div className="size-full">
        <Homepage
          onStartReview={async (exp) => {
            setRunError(null);
            const { run_id } = await createRun(exp);
            setRunId(run_id);
            persistRunId(run_id);
            setExperiment(exp);
            const r = await fetchRun(run_id);
            setRun(r);
            setStage("literature-review");
          }}
        />
      </div>
    );
  }

  if (stage === "literature-review") {
    return (
      <div className="size-full">
        <LiteratureReview
          experiment={experiment}
          runId={runId}
          onHomeClick={() => setStage("homepage")}
          onProceedToDashboard={() => {
            void refreshRun();
            setStage("dashboard");
          }}
        />
      </div>
    );
  }

  const artifacts = run?.artifacts ?? {};
  const scientificIntent = asRecord(artifacts.scientific_intent);
  const priorWork = asRecord(artifacts.prior_work);
  const negativeResults = asRecord(artifacts.negative_results);
  const claimGraph = asRecord(artifacts.claim_graph);
  const experimentIr = asRecord(artifacts.experiment_ir);
  const feasibilityReport = asRecord(artifacts.feasibility_report);
  const valueScore = asRecord(artifacts.value_score);
  const protocol = asRecord(artifacts.protocol);
  const schedule = asRecord(artifacts.schedule);
  const executionLog = asRecord(artifacts.execution_log);
  const chartSeriesRaw = executionLog?.series_for_charts;
  const chartSeries =
    Array.isArray(chartSeriesRaw) && chartSeriesRaw.length > 0 && typeof chartSeriesRaw[0] === "object"
      ? asRecord(chartSeriesRaw[0] as object)
      : null;
  const failureRecovery = asRecord(artifacts.failure_recovery_plan);
  const validationReport = asRecord(artifacts.validation_report);
  const interpretation = asRecord(artifacts.interpretation);
  const normalizedResults = asRecord(artifacts.normalized_results);
  const normalizedFidelity = typeof normalizedResults?.fidelity === "string" ? normalizedResults.fidelity : null;
  const normalizedOrigin = typeof normalizedResults?.origin === "string" ? normalizedResults.origin : null;
  const procedureTraceRaw = normalizedResults?.procedure_trace;
  const procedureTrace = Array.isArray(procedureTraceRaw)
    ? procedureTraceRaw.filter((x): x is Record<string, unknown> => typeof x === "object" && x !== null)
    : [];
  const observationsRaw = normalizedResults?.observations;
  const observations = Array.isArray(observationsRaw)
    ? observationsRaw.filter((x): x is Record<string, unknown> => typeof x === "object" && x !== null)
    : [];
  const nextRec = asRecord(artifacts.next_experiment_recommendation);
  const pipelineSummaries = asRecord(artifacts.pipeline_summaries);
  const artifactSummaries = asRecord(artifacts.artifact_summaries);

  const headerStatus = run ? mapRunStateToHeaderStatus(run.state) : "Draft";
  const showApprove = run?.state === "AWAITING_HUMAN_APPROVAL";
  const canExport =
    Boolean(run?.artifacts?.report) || run?.state === "MEMORY_UPDATED" || run?.state === "REPORT_GENERATED";
  const terminalStates = new Set(["MEMORY_UPDATED", "REPORT_GENERATED"]);
  const canAdvance =
    Boolean(runId) &&
    run &&
    !terminalStates.has(run.state) &&
    run.state !== "AWAITING_HUMAN_APPROVAL";

  const sectionSubtabs: Record<DashboardSection, Array<{ id: string; label: string }>> = {
    intake: [
      { id: "goal", label: "Research Goal" },
      { id: "prior-work", label: "Prior Work & Novelty" },
      { id: "claim-graph", label: "Claim Graph" },
    ],
    planning: [
      { id: "compiler", label: "Experiment Compiler" },
      { id: "simulation", label: "Simulation Controls" },
      { id: "schedule", label: "Schedule" },
    ],
    runtime: [
      { id: "execution", label: "Execution" },
      { id: "recovery", label: "Failure & Recovery" },
      { id: "validation", label: "Data Validation" },
      { id: "results", label: "Results" },
    ],
    outcomes: [
      { id: "summary", label: "Run Summary" },
      { id: "next", label: "Next Experiment" },
      { id: "provenance", label: "Provenance Log" },
      { id: "compare", label: "Compare Runs" },
    ],
  };

  const selectedTab = sectionTabs[currentSection];

  const summaryFor = (section: "planning" | "runtime" | "outcomes") => {
    const value = asRecord(pipelineSummaries?.[section]);
    return {
      summary: typeof value?.summary === "string" ? value.summary : null,
      generatedAt: typeof value?.generated_at === "string" ? value.generated_at : null,
    };
  };

  const artifactSummaryFor = (artifactKey: string) => {
    const value = asRecord(artifactSummaries?.[artifactKey]);
    return {
      summary: typeof value?.summary === "string" ? value.summary : null,
      generatedAt: typeof value?.generated_at === "string" ? value.generated_at : null,
    };
  };

  const renderPipelineInspector = () => {
    if (!run) return null;
    if (currentSection === "planning") {
      const summary = summaryFor("planning");
      return (
        <PipelineJsonInspector
          title="Planning Pipeline JSON"
          summary={summary.summary}
          generatedAt={summary.generatedAt}
          data={{
            pipeline: run.pipeline.planning,
            artifacts: { experiment_ir: experimentIr, feasibility_report: feasibilityReport, value_score: valueScore, protocol, schedule },
          }}
        />
      );
    }
    if (currentSection === "runtime") {
      const summary = summaryFor("runtime");
      return (
        <PipelineJsonInspector
          title="Runtime Pipeline JSON"
          summary={summary.summary}
          generatedAt={summary.generatedAt}
          data={{
            pipeline: run.pipeline.runtime,
            artifacts: {
              execution_log: executionLog,
              failure_recovery_plan: failureRecovery,
              validation_report: validationReport,
              normalized_results: normalizedResults,
              interpretation,
            },
          }}
        />
      );
    }
    if (currentSection === "outcomes") {
      const summary = summaryFor("outcomes");
      return (
        <PipelineJsonInspector
          title="Outcomes & Provenance JSON"
          summary={summary.summary}
          generatedAt={summary.generatedAt}
          data={{
            pipeline: run.pipeline.outcomes,
            artifacts: {
              next_experiment_recommendation: nextRec,
              report: asRecord(artifacts.report),
              memory_update: asRecord(artifacts.memory_update),
              provenance: run.provenance,
            },
          }}
        />
      );
    }
    return null;
  };

  const renderPanel = () => {
    switch (currentSection) {
      case "intake":
        switch (sectionTabs.intake) {
          case "goal":
            return (
              <div>
                <h2 className="text-xl text-stone-900 mb-6">Research Goal</h2>
                <ResearchGoalPanel userGoal={run?.user_goal ?? experiment} intent={scientificIntent} />
              </div>
            );
          case "prior-work":
            return (
              <div>
                <h2 className="text-xl text-stone-900 mb-6">Prior Work & Novelty</h2>
                <PriorWorkPanel
                  priorWork={priorWork}
                  negativeResults={negativeResults}
                  valueScore={valueScore}
                  artifactSummaries={artifactSummaries}
                />
              </div>
            );
          case "claim-graph":
            return (
              <div>
                <h2 className="text-xl text-stone-900 mb-6">Claim Graph</h2>
                <ClaimGraphPanel claimGraph={claimGraph} onSelectHypothesis={handleSelectHypothesis} busy={actionBusy} />
              </div>
            );
          default:
            return null;
        }
      case "planning":
        switch (sectionTabs.planning) {
          case "compiler":
            return (
              <div>
                <h2 className="text-xl text-stone-900 mb-6">Experiment Compiler</h2>
                <CompilerPanel
                  experimentIr={experimentIr}
                  feasibilityReport={feasibilityReport}
                  protocol={protocol}
                  artifactSummaries={artifactSummaries}
                />
              </div>
            );
          case "simulation":
            return (
              <div>
                <h2 className="text-xl text-stone-900 mb-6">Simulation Controls</h2>
                <SimulationControlsPanel
                  current={asRecord(artifacts.simulation_overrides)}
                  onApply={handleApplySimulationControls}
                  busy={actionBusy}
                />
              </div>
            );
          case "schedule":
            return (
              <div>
                <h2 className="text-xl text-stone-900 mb-6">Schedule</h2>
                <SchedulePanel
                  schedule={schedule}
                  protocol={protocol}
                  summary={artifactSummaryFor("schedule").summary}
                  generatedAt={artifactSummaryFor("schedule").generatedAt}
                />
              </div>
            );
          default:
            return null;
        }
      case "runtime":
        switch (sectionTabs.runtime) {
          case "execution":
            return (
              <div>
                <h2 className="text-xl text-stone-900 mb-6">Execution</h2>
                <ExecutionPanel
                  artifact={executionLog}
                  summary={artifactSummaryFor("execution_log").summary}
                  generatedAt={artifactSummaryFor("execution_log").generatedAt}
                />
              </div>
            );
          case "recovery":
            return (
              <div>
                <h2 className="text-xl text-stone-900 mb-6">Failure & Recovery</h2>
                <FailureRecoveryPanel
                  artifact={failureRecovery}
                  summary={artifactSummaryFor("failure_recovery_plan").summary}
                  generatedAt={artifactSummaryFor("failure_recovery_plan").generatedAt}
                />
              </div>
            );
          case "validation":
            return (
              <div>
                <h2 className="text-xl text-stone-900 mb-6">Data Validation</h2>
                <DataValidationPanel
                  artifact={validationReport}
                  summary={artifactSummaryFor("validation_report").summary}
                  generatedAt={artifactSummaryFor("validation_report").generatedAt}
                />
              </div>
            );
          case "results":
            return (
              <div>
                <h2 className="text-xl text-stone-900 mb-6">Results</h2>
                <ResultsPanel
                  artifact={interpretation}
                  chartSeries={chartSeries}
                  summary={artifactSummaryFor("interpretation").summary}
                  generatedAt={artifactSummaryFor("interpretation").generatedAt}
                  procedureTrace={procedureTrace}
                  observations={observations}
                  fidelity={normalizedFidelity}
                  origin={normalizedOrigin}
                />
              </div>
            );
          default:
            return null;
        }
      case "outcomes":
        switch (sectionTabs.outcomes) {
          case "summary":
            return (
              <div>
                <h2 className="text-xl text-stone-900 mb-6">Run Summary</h2>
                {run ? <RunSummaryPanel run={run} /> : <div className="text-sm text-stone-600">Run not loaded.</div>}
              </div>
            );
          case "next":
            return (
              <div>
                <h2 className="text-xl text-stone-900 mb-6">Next Experiment</h2>
                <NextExperimentPanel
                  recommendation={nextRec}
                  summary={artifactSummaryFor("next_experiment_recommendation").summary}
                  generatedAt={artifactSummaryFor("next_experiment_recommendation").generatedAt}
                />
              </div>
            );
          case "provenance":
            return (
              <div>
                <h2 className="text-xl text-stone-900 mb-6">Provenance Log</h2>
                <ProvenanceLogPanel events={run?.provenance} />
              </div>
            );
          case "compare":
            return (
              <div>
                <h2 className="text-xl text-stone-900 mb-6">Compare Runs</h2>
                <CompareRunsPanel baseRun={run} />
              </div>
            );
          default:
            return null;
        }
      default:
        return null;
    }
  };

  return (
    <div className="size-full flex flex-col bg-yellow-50">
      <Header
        runId={runId ?? "—"}
        experimentName={run?.user_goal || experiment || "Active run"}
        workflowState={run?.state}
        status={headerStatus}
        onHomeClick={() => setStage("homepage")}
        onAdvance={canAdvance ? handleAdvance : undefined}
        onApprove={runId ? handleApprove : undefined}
        onExportSelection={runId && canExport ? handleExportSelection : undefined}
        onDemoWalkthrough={canAdvance || showApprove ? handleDemoWalkthrough : undefined}
        showApprove={showApprove}
        actionBusy={actionBusy}
      />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          currentSection={currentSection}
          onSectionChange={setCurrentSection}
          sectionSubtabs={sectionSubtabs}
          currentSubtab={sectionTabs}
          onSubtabChange={(section, tabId) => {
            setSectionTabs((prev) => ({ ...prev, [section]: tabId } as SectionTabMap));
          }}
        />

        <main className="flex-1 overflow-y-auto p-8 bg-gradient-to-br from-amber-50 via-yellow-50 to-orange-50 relative">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-green-100/20 via-transparent to-transparent pointer-events-none" />
          <div className="absolute top-20 right-20 w-96 h-96 bg-green-200/10 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute bottom-20 left-20 w-96 h-96 bg-emerald-200/10 rounded-full blur-3xl pointer-events-none" />

          <div className="max-w-7xl mx-auto relative z-10 space-y-4">
            {run && <ExperimentBriefPanel run={run} />}
            <ProcedureProgressPanel trace={procedureTrace} />

            {runError && (
              <div className="mb-4 rounded-lg border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-900">{runError}</div>
            )}
            {!run && runId && (
              <div className="mb-4 text-sm text-stone-600">Loading run {runId}…</div>
            )}
            {renderPanel()}
            {renderPipelineInspector()}
            <StageNarrativeBanner section={currentSection} tab={selectedTab} />
          </div>
        </main>
      </div>
    </div>
  );
}
