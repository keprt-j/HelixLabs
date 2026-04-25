import { useState } from "react";
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

type AppStage = "homepage" | "literature-review" | "dashboard";

export default function App() {
  const [stage, setStage] = useState<AppStage>("homepage");
  const [experiment, setExperiment] = useState("");
  const [currentSection, setCurrentSection] = useState("goal");

  if (stage === "homepage") {
    return (
      <div className="size-full">
        <Homepage
          onStartReview={(exp) => {
            setExperiment(exp);
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
          onProceedToDashboard={() => setStage("dashboard")}
        />
      </div>
    );
  }

  const renderPanel = () => {
    switch (currentSection) {
      case "goal":
        return (
          <div>
            <h2 className="text-xl text-stone-900 mb-6">Research Goal</h2>
            <ResearchGoalPanel />
            <div className="mt-6">
              <h2 className="text-xl text-stone-900 mb-6">Prior Work & Novelty</h2>
              <PriorWorkPanel />
            </div>
          </div>
        );
      case "claim-graph":
        return (
          <div>
            <h2 className="text-xl text-stone-900 mb-6">Claim Graph</h2>
            <ClaimGraphPanel />
          </div>
        );
      case "compiler":
        return (
          <div>
            <h2 className="text-xl text-stone-900 mb-6">Experiment Compiler</h2>
            <CompilerPanel />
          </div>
        );
      case "schedule":
        return (
          <div>
            <h2 className="text-xl text-stone-900 mb-6">Schedule</h2>
            <SchedulePanel />
          </div>
        );
      case "execution":
        return (
          <div>
            <h2 className="text-xl text-stone-900 mb-6">Execution</h2>
            <ExecutionPanel />
            <div className="mt-6">
              <h2 className="text-xl text-stone-900 mb-6">Failure & Recovery</h2>
              <FailureRecoveryPanel />
            </div>
          </div>
        );
      case "validation":
        return (
          <div>
            <h2 className="text-xl text-stone-900 mb-6">Data Validation</h2>
            <DataValidationPanel />
          </div>
        );
      case "results":
        return (
          <div>
            <h2 className="text-xl text-stone-900 mb-6">Results</h2>
            <ResultsPanel />
          </div>
        );
      case "next":
        return (
          <div>
            <h2 className="text-xl text-stone-900 mb-6">Next Experiment</h2>
            <NextExperimentPanel />
          </div>
        );
      case "provenance":
        return (
          <div>
            <h2 className="text-xl text-stone-900 mb-6">Provenance Log</h2>
            <ProvenanceLogPanel />
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="size-full flex flex-col bg-yellow-50">
      <Header
        runId="RUN-4729"
        experimentName={experiment || "Fe-doped LLZO ionic conductivity study"}
        status="Running"
        onHomeClick={() => setStage("homepage")}
      />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          currentSection={currentSection}
          onSectionChange={setCurrentSection}
        />

        <main className="flex-1 overflow-y-auto p-8 bg-gradient-to-br from-amber-50 via-yellow-50 to-orange-50 relative">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-green-100/20 via-transparent to-transparent pointer-events-none" />
          <div className="absolute top-20 right-20 w-96 h-96 bg-green-200/10 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute bottom-20 left-20 w-96 h-96 bg-emerald-200/10 rounded-full blur-3xl pointer-events-none" />

          <div className="max-w-7xl mx-auto relative z-10">
            {renderPanel()}
          </div>
        </main>
      </div>
    </div>
  );
}