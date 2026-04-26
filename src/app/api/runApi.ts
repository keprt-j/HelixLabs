import type { HelixRun, RunListItem } from "../types/run";

export type SimulationOverrides = {
  n_replicates?: number;
  noise_scale_relative?: number;
  design_density?: "coarse" | "medium" | "fine";
  seed?: number;
};

export function getApiBase(): string {
  return (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "http://127.0.0.1:8000";
}

async function parseJson<T>(res: Response): Promise<T> {
  const text = await res.text();
  try {
    return JSON.parse(text) as T;
  } catch {
    throw new Error(res.ok ? "Invalid JSON from API" : `${res.status}: ${text.slice(0, 200)}`);
  }
}

export async function createRun(
  userGoal: string,
  opts: { simulationOverrides?: SimulationOverrides } = {},
): Promise<{ run_id: string; state: string }> {
  const base = getApiBase();
  const res = await fetch(`${base}/api/runs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_goal: userGoal,
      simulation_overrides: opts.simulationOverrides,
    }),
  });
  if (!res.ok) {
    throw new Error(`Unable to create run (${res.status})`);
  }
  return parseJson(res);
}

export async function fetchRun(runId: string): Promise<HelixRun> {
  const base = getApiBase();
  const res = await fetch(`${base}/api/runs/${encodeURIComponent(runId)}`);
  if (!res.ok) {
    throw new Error(`Unable to fetch run (${res.status})`);
  }
  const data = await parseJson<{ run: HelixRun }>(res);
  if (!data?.run) {
    throw new Error("Run payload missing");
  }
  return data.run;
}

export async function fetchRunList(limit = 50): Promise<RunListItem[]> {
  const base = getApiBase();
  const res = await fetch(`${base}/api/runs?limit=${encodeURIComponent(String(limit))}`);
  if (!res.ok) {
    throw new Error(`Unable to list runs (${res.status})`);
  }
  const data = await parseJson<{ runs: RunListItem[] }>(res);
  return Array.isArray(data?.runs) ? data.runs : [];
}

export async function advanceRun(runId: string): Promise<HelixRun> {
  const base = getApiBase();
  const res = await fetch(`${base}/api/runs/${encodeURIComponent(runId)}/advance`, { method: "POST" });
  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    throw new Error(detail ? `Advance failed (${res.status}): ${detail.slice(0, 300)}` : `Advance failed (${res.status})`);
  }
  const data = await parseJson<{ run: HelixRun }>(res);
  return data.run;
}

export async function approveRun(
  runId: string,
  opts: { approved_by?: string; notes?: string } = {},
): Promise<HelixRun> {
  const base = getApiBase();
  const res = await fetch(`${base}/api/runs/${encodeURIComponent(runId)}/approve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      approved: true,
      approved_by: opts.approved_by ?? "ui_user",
      notes: opts.notes ?? "",
    }),
  });
  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    throw new Error(detail ? `Approve failed (${res.status}): ${detail.slice(0, 300)}` : `Approve failed (${res.status})`);
  }
  const data = await parseJson<{ run: HelixRun }>(res);
  return data.run;
}

export async function fetchReportRun(runId: string): Promise<HelixRun> {
  const base = getApiBase();
  const res = await fetch(`${base}/api/runs/${encodeURIComponent(runId)}/report`);
  if (!res.ok) {
    throw new Error(`Report not available (${res.status})`);
  }
  const data = await parseJson<{ run: HelixRun }>(res);
  return data.run;
}

export async function setRunSimulationOverrides(runId: string, simulationOverrides: SimulationOverrides): Promise<HelixRun> {
  const base = getApiBase();
  const res = await fetch(`${base}/api/runs/${encodeURIComponent(runId)}/simulation-overrides`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ simulation_overrides: simulationOverrides }),
  });
  if (!res.ok) {
    throw new Error(`Unable to set simulation overrides (${res.status})`);
  }
  const data = await parseJson<{ run: HelixRun }>(res);
  return data.run;
}

export async function replanRun(runId: string): Promise<HelixRun> {
  const base = getApiBase();
  const res = await fetch(`${base}/api/runs/${encodeURIComponent(runId)}/replan`, { method: "POST" });
  if (!res.ok) {
    throw new Error(`Unable to replan run (${res.status})`);
  }
  const data = await parseJson<{ run: HelixRun }>(res);
  return data.run;
}

export async function selectHypothesis(runId: string, hypothesisId: string): Promise<HelixRun> {
  const base = getApiBase();
  const res = await fetch(`${base}/api/runs/${encodeURIComponent(runId)}/select-hypothesis`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ hypothesis_id: hypothesisId }),
  });
  if (!res.ok) {
    throw new Error(`Unable to select hypothesis (${res.status})`);
  }
  const data = await parseJson<{ run: HelixRun }>(res);
  return data.run;
}
