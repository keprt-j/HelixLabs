import type { RunPayload } from "./types";

export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {"Content-Type": "application/json", ...(init?.headers ?? {})},
    ...init
  });
  const payload = await response.json();
  if (!response.ok) {
    const message = payload?.error?.message ?? `Request failed with ${response.status}`;
    throw new Error(message);
  }
  return payload as T;
}

export async function createRun(userGoal: string): Promise<RunPayload> {
  const created = await request<{run: RunPayload["run"]}>("/api/runs", {
    method: "POST",
    body: JSON.stringify({user_goal: userGoal})
  });
  return request<RunPayload>(`/api/runs/${created.run.id}`);
}

export async function getRun(runId: string): Promise<RunPayload> {
  return request<RunPayload>(`/api/runs/${runId}`);
}

export async function advanceRun(runId: string): Promise<void> {
  await request(`/api/runs/${runId}/advance`, {method: "POST"});
}

export async function approveRun(runId: string): Promise<void> {
  await request(`/api/runs/${runId}/approve`, {
    method: "POST",
    body: JSON.stringify({approved: true, approved_by: "demo_user", notes: "Approved narrowed screen after prior-work check."})
  });
}
