import Head from "next/head";
import type React from "react";
import { useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  Beaker,
  Check,
  ChevronRight,
  Database,
  FileText,
  FlaskConical,
  GitBranch,
  Play,
  RefreshCcw,
  Search,
  ShieldCheck,
  Wrench
} from "lucide-react";
import { advanceRun, approveRun, createRun, forceFallbackSearch, getRun } from "../lib/api";
import { RunPayload, RunState, stateSequence } from "../lib/types";

const canonicalGoal =
  "Find a low-cost cobalt-free cathode material and test whether Mn doping improves conductivity without hurting stability.";

type PanelProps = {
  title: string;
  icon: React.ReactNode;
  ready: boolean;
  children: React.ReactNode;
};

export default function Home() {
  const [goal, setGoal] = useState(canonicalGoal);
  const [payload, setPayload] = useState<RunPayload | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const artifacts = payload?.artifacts ?? {};
  const currentIndex = payload ? stateSequence.indexOf(payload.run.state) : -1;
  const progressPercent = payload ? Math.round((currentIndex / (stateSequence.length - 1)) * 100) : 0;

  const nextAction = useMemo(() => {
    if (!payload) return "Create run";
    if (payload.run.state === "AWAITING_HUMAN_APPROVAL") return "Approve";
    if (payload.run.state === "MEMORY_UPDATED") return "Complete";
    return "Advance";
  }, [payload]);

  async function refresh(runId = payload?.run.id) {
    if (!runId) return;
    setPayload(await getRun(runId));
  }

  async function runAction(action: () => Promise<void | RunPayload>) {
    setBusy(true);
    setError(null);
    try {
      const result = await action();
      if (result) setPayload(result);
      else await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setBusy(false);
    }
  }

  async function runDemoToEnd() {
    setBusy(true);
    setError(null);
    try {
      let nextPayload = payload ?? (await createRun(goal));
      setPayload(nextPayload);
      for (let i = 0; i < 40 && nextPayload.run.state !== "MEMORY_UPDATED"; i += 1) {
        if (nextPayload.run.state === "AWAITING_HUMAN_APPROVAL") {
          await approveRun(nextPayload.run.id);
        } else {
          await advanceRun(nextPayload.run.id);
        }
        nextPayload = await getRun(nextPayload.run.id);
        setPayload(nextPayload);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Demo run failed");
    } finally {
      setBusy(false);
    }
  }

  async function primaryAction() {
    if (!payload) return runAction(() => createRun(goal));
    if (payload.run.state === "AWAITING_HUMAN_APPROVAL") return runAction(async () => approveRun(payload.run.id));
    if (payload.run.state === "MEMORY_UPDATED") return undefined;
    return runAction(async () => advanceRun(payload.run.id));
  }

  return (
    <>
      <Head>
        <title>HelixLabs Console</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      <main className="shell">
        <section className="topbar">
          <div>
            <p className="eyebrow">HelixLabs</p>
            <h1>Cloud-lab operating system for autonomous science</h1>
          </div>
          <div className="statusBlock">
            <span className="statusLabel">Run state</span>
            <strong>{payload?.run.state ?? "NOT_CREATED"}</strong>
          </div>
        </section>

        <section className="commandBand">
          <div className="goalBox">
            <label htmlFor="goal">Research Goal</label>
            <textarea id="goal" value={goal} onChange={(event) => setGoal(event.target.value)} />
          </div>
          <div className="actions">
            <button className="primary" onClick={primaryAction} disabled={busy || nextAction === "Complete"}>
              {nextAction === "Approve" ? <ShieldCheck size={18} /> : <ChevronRight size={18} />}
              {nextAction}
            </button>
            <button onClick={runDemoToEnd} disabled={busy}>
              <Play size={18} />
              Run demo
            </button>
            <button
              onClick={() => payload && runAction(async () => forceFallbackSearch(payload.run.id))}
              disabled={busy || !payload || payload.run.state !== "GOAL_PARSED"}
              title="Force cached literature fallback after goal parsing"
            >
              <RefreshCcw size={18} />
              Fallback search
            </button>
          </div>
          {error && <div className="error"><AlertTriangle size={16} />{error}</div>}
        </section>

        <section className="progressBand">
          <div className="meter">
            <span style={{ width: `${progressPercent}%` }} />
          </div>
          <div className="stateGrid">
            {stateSequence.map((state, index) => (
              <StatePill key={state} state={state} active={payload?.run.state === state} complete={index <= currentIndex} />
            ))}
          </div>
        </section>

        <section className="dashboard">
          <Panel title="Literature / Prior Work Search" icon={<Search size={18} />} ready={Boolean(artifacts.retrieved_papers)}>
            <Metric label="Retrieval" value={artifacts.retrieval_mode ?? "pending"} />
            <List items={(artifacts.retrieved_papers ?? []).map((paper: any) => `${paper.title} (${paper.retrieval_mode})`)} />
          </Panel>

          <Panel title="Evidence and Experiment Matches" icon={<GitBranch size={18} />} ready={Boolean(artifacts.prior_work_match)}>
            <p>{artifacts.prior_work_match?.gap ?? "Prior-work gap will appear here."}</p>
            <List items={(artifacts.prior_work_match?.matches ?? []).map((item: any) => `${item.overlap}: ${(item.tested_conditions ?? []).join(", ")} - ${item.reported_result}`)} />
          </Panel>

          <Panel title="Negative Results" icon={<AlertTriangle size={18} />} ready={Boolean(artifacts.negative_results)}>
            <List items={(artifacts.negative_results ?? []).map((item: any) => `${item.failed_condition}: ${item.failure_type}. ${item.recommendation}`)} />
          </Panel>

          <Panel title="Claim Graph" icon={<GitBranch size={18} />} ready={Boolean(artifacts.claim_graph)}>
            <p className="callout">{artifacts.claim_graph?.main_hypothesis ?? "Waiting for claims."}</p>
            <List items={(artifacts.claim_graph?.claims ?? []).map((claim: any) => `${claim.id} ${claim.status}: ${claim.claim}`)} />
          </Panel>

          <Panel title="Experiment IR" icon={<FlaskConical size={18} />} ready={Boolean(artifacts.experiment_ir)}>
            <Metric label="Material" value={artifacts.experiment_ir?.material ?? "pending"} />
            <Metric label="Mn fractions" value={(artifacts.experiment_ir?.variables?.mn_fraction ?? []).join(", ") || "pending"} />
            <List items={artifacts.experiment_ir?.controls ?? []} />
          </Panel>

          <Panel title="Feasibility and Value Scores" icon={<Activity size={18} />} ready={Boolean(artifacts.value_score || artifacts.feasibility_report)}>
            <ScoreRow label="Novelty" value={artifacts.value_score?.novelty_score} />
            <ScoreRow label="Redundancy" value={artifacts.value_score?.redundancy_score} />
            <ScoreRow label="Value" value={artifacts.value_score?.overall_experiment_value} />
            <List items={(artifacts.feasibility_report?.issues ?? []).map((issue: any) => `${issue.severity}: ${issue.issue}`)} />
          </Panel>

          <Panel title="Protocol" icon={<FileText size={18} />} ready={Boolean(artifacts.protocol)}>
            <List items={(artifacts.protocol?.steps ?? []).map((step: any) => `${step.step_id}: ${step.name} (${step.resource_type}, ${step.duration_minutes} min)`)} />
          </Panel>

          <Panel title="Cloud-Lab Schedule" icon={<Beaker size={18} />} ready={Boolean(artifacts.schedule)}>
            <List items={(artifacts.schedule?.scheduled_tasks ?? []).map((task: any) => `${task.step_id} on ${task.resource_id}: ${task.start}-${task.end}`)} />
          </Panel>

          <Panel title="Approval Gate" icon={<ShieldCheck size={18} />} ready={Boolean(artifacts.approval_gate || artifacts.approval_event)}>
            <p>{artifacts.approval_event ? `Approved by ${artifacts.approval_event.approved_by}` : artifacts.approval_gate?.summary ?? "Approval gate opens after scheduling."}</p>
          </Panel>

          <Panel title="Execution Monitor" icon={<Activity size={18} />} ready={Boolean(artifacts.execution_log)}>
            <List items={(artifacts.execution_log?.events ?? []).map((event: any) => `${event.timestamp} ${event.step_id}: ${event.event_type} - ${event.message}`)} />
          </Panel>

          <Panel title="Failure Recovery" icon={<Wrench size={18} />} ready={Boolean(artifacts.failure_recovery_plan)}>
            <p className="callout">{artifacts.failure_recovery_plan?.selected_recovery ?? "Recovery decision pending."}</p>
            <List items={(artifacts.failure_recovery_plan?.recovery_options ?? []).map((option: any) => `${option.action}: score ${option.score}, cost ${option.cost_minutes} min`)} />
          </Panel>

          <Panel title="Data Stent Validation and Repair" icon={<Database size={18} />} ready={Boolean(artifacts.validation_report)}>
            <List items={(artifacts.validation_report?.issues ?? []).map((issue: any) => `${issue.found} -> ${issue.expected}`)} />
            <ResultTable rows={artifacts.repaired_results ?? []} />
          </Panel>

          <Panel title="Result Interpretation" icon={<Check size={18} />} ready={Boolean(artifacts.interpretation)}>
            <List items={artifacts.interpretation?.observed_results ?? []} />
            <p className="callout">{artifacts.interpretation?.uncertainty ?? "Interpretation pending."}</p>
          </Panel>

          <Panel title="Next Experiment Recommendation" icon={<ChevronRight size={18} />} ready={Boolean(artifacts.next_experiment_recommendation)}>
            <p className="callout">{artifacts.next_experiment_recommendation?.selected_next_experiment ?? "Recommendation pending."}</p>
            <List items={(artifacts.next_experiment_recommendation?.candidate_next_experiments ?? []).map((item: any) => `${item.name}: ${(item.conditions ?? []).join(", ")} (score ${item.score})`)} />
          </Panel>

          <Panel title="Provenance Report" icon={<FileText size={18} />} ready={Boolean(artifacts.report)}>
            <List items={(artifacts.report?.sections ?? []).map((section: any) => `${section.title}: ${section.content}`)} />
            <Metric label="Events" value={payload?.provenance_events.length.toString() ?? "0"} />
          </Panel>
        </section>
      </main>
    </>
  );
}

function StatePill({ state, active, complete }: { state: RunState; active: boolean; complete: boolean }) {
  return <span className={`statePill ${active ? "active" : ""} ${complete ? "complete" : ""}`}>{state.split("_").join(" ")}</span>;
}

function Panel({ title, icon, ready, children }: PanelProps) {
  return (
    <article className={`panel ${ready ? "ready" : ""}`}>
      <header>
        <span>{icon}</span>
        <h2>{title}</h2>
      </header>
      <div className="panelBody">{children}</div>
    </article>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function ScoreRow({ label, value }: { label: string; value?: number }) {
  const percent = Math.round((value ?? 0) * 100);
  return (
    <div className="scoreRow">
      <span>{label}</span>
      <div><i style={{ width: `${percent}%` }} /></div>
      <strong>{value === undefined ? "pending" : value.toFixed(2)}</strong>
    </div>
  );
}

function List({ items }: { items: string[] }) {
  if (!items.length) return <p className="muted">Pending.</p>;
  return (
    <ul>
      {items.map((item, index) => <li key={`${item}-${index}`}>{item}</li>)}
    </ul>
  );
}

function ResultTable({ rows }: { rows: Array<Record<string, any>> }) {
  if (!rows.length) return null;
  return (
    <table>
      <thead>
        <tr>
          <th>Candidate</th>
          <th>Mn</th>
          <th>Hull</th>
          <th>Conductivity</th>
          <th>Stable</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.candidate_id}>
            <td>{row.candidate_id}</td>
            <td>{row.mn_fraction}</td>
            <td>{row.energy_above_hull}</td>
            <td>{row.conductivity_proxy}</td>
            <td>{String(row.stability_pass)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
