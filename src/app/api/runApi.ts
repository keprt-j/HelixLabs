import type { HelixRun } from "../types/run";

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

export async function createRun(userGoal: string): Promise<{ run_id: string; state: string }> {
  const base = getApiBase();
  const res = await fetch(`${base}/api/runs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_goal: userGoal }),
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
