# HelixLabs

HelixLabs is a cloud-lab operating system for autonomous science. It compiles scientific intent into evidence-aware, non-redundant, scheduled, executable, validated, recoverable experiments, then recommends the next highest-value experiment.

The MVP implements the canonical materials-discovery demo for cobalt-free cathode optimization with LiFePO4 and Mn doping.

## What Is Implemented

- FastAPI backend with typed Pydantic v2 schemas.
- JSON persistence under `data/runtime/`.
- Public Crossref literature lookup with cached fallback seed data.
- Prior-work matching for already tested 0%, 5%, 10%, and failed 20% Mn conditions.
- Negative-results memory.
- Claim graph with weakest high-value claim selection.
- Experiment IR compiler for 12%, 14%, and 16% Mn.
- Feasibility validator and novelty/redundancy/value scorer.
- Structured protocol generator.
- Dependency-aware simulated lab resource scheduler.
- Human approval checkpoint.
- Simulated execution with `property_predictor_timeout`.
- Failure recovery selecting `retry_failed_condition`.
- Data stent validation and repair for drifted result columns.
- Result interpretation with observations, evidence, inference, uncertainty, and limitations separated.
- Next-experiment planner recommending 14.5%, 15.0%, and 15.5% Mn.
- Provenance report and experiment memory update.
- Next.js dashboard with all required panels visible from one screen.

## Repo Layout

```text
apps/
  api/          FastAPI app
  web/          Next.js dashboard
packages/      Backend services and typed models
data/           Seed data, schemas, and runtime JSON persistence
tests/          Pytest coverage for workflow, fallback, compiler, and data stent
```

## Environment

Copy `.env.example` to `.env` if you want to customize settings.

```powershell
Copy-Item .env.example .env
```

The demo does not require API keys. Live literature search uses Crossref when available and falls back to `data/sample_literature.json` when offline or forced from the UI.

## Backend Setup

From the repo root:

```powershell
cd apps/api
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

If you already have the dependencies installed globally, this also works:

```powershell
cd apps/api
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Health check:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
```

## Frontend Setup

In another terminal:

```powershell
cd apps/web
npm install
npm run dev -- --hostname 127.0.0.1 --port 3000
```

Open:

```text
http://127.0.0.1:3000
```

## Demo Script

1. Open the dashboard.
2. Keep the canonical goal:

```text
Find a low-cost cobalt-free cathode material and test whether Mn doping improves conductivity without hurting stability.
```

3. Click `Run demo` to execute the full lifecycle.
4. Watch the state machine progress through `MEMORY_UPDATED`.
5. Confirm the visible outputs:
   - prior tests at 0%, 5%, and 10% Mn
   - negative stability result at 20% Mn
   - narrowed experiment at 12%, 14%, and 16% Mn
   - human approval gate
   - simulated timeout and recovery
   - schema drift detection and repair
   - interpretation showing 12% and 14% pass, 16% fails
   - next recommendation at 14.5%, 15.0%, and 15.5% Mn
   - provenance report

You can also step manually with `Create run`, `Advance`, and `Approve`.

## API Demo

```powershell
$goal = "Find a low-cost cobalt-free cathode material and test whether Mn doping improves conductivity without hurting stability."
$created = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/runs -ContentType "application/json" -Body (@{user_goal=$goal} | ConvertTo-Json)
$runId = $created.run.id

for ($i = 0; $i -lt 30; $i++) {
  $run = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/runs/$runId"
  if ($run.run.state -eq "MEMORY_UPDATED") { break }
  if ($run.run.state -eq "AWAITING_HUMAN_APPROVAL") {
    Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/runs/$runId/approve" -ContentType "application/json" -Body (@{approved=$true; approved_by="demo_user"; notes="Approved narrowed screen."} | ConvertTo-Json) | Out-Null
  } else {
    Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/runs/$runId/advance" | Out-Null
  }
}

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/runs/$runId" | ConvertTo-Json -Depth 8
```

## Tests and Validation

Commands run during implementation:

```powershell
pytest
cd apps/web
npm run typecheck
npm run build
npm audit
```

Observed results:

- `pytest`: 4 passed.
- `npm run typecheck`: passed.
- `npm run build`: passed with Next.js 16.2.4.
- `npm audit`: 0 vulnerabilities after pinning Next.js 16.2.4 and overriding PostCSS to 8.5.10.
- Local backend smoke: `GET /api/health` returned `status: ok`.
- Local frontend smoke: `GET http://127.0.0.1:3000` returned HTTP 200.
- End-to-end API smoke reached `MEMORY_UPDATED` with 23 provenance events.

## Main Endpoints

```text
POST /api/runs
GET  /api/runs/{run_id}
POST /api/runs/{run_id}/advance
POST /api/runs/{run_id}/approve
GET  /api/runs/{run_id}/report
```

The detailed stage endpoints from `API_CONTRACTS.md` are also implemented:

```text
POST /api/runs/{run_id}/parse-goal
POST /api/runs/{run_id}/search-literature
POST /api/runs/{run_id}/match-prior-work
POST /api/runs/{run_id}/check-negative-results
POST /api/runs/{run_id}/build-claim-graph
POST /api/runs/{run_id}/compile-ir
POST /api/runs/{run_id}/validate-feasibility
POST /api/runs/{run_id}/score-value
POST /api/runs/{run_id}/generate-protocol
POST /api/runs/{run_id}/schedule
POST /api/runs/{run_id}/execute
POST /api/runs/{run_id}/recover
POST /api/runs/{run_id}/validate-results
POST /api/runs/{run_id}/interpret
POST /api/runs/{run_id}/recommend-next
POST /api/runs/{run_id}/update-memory
```

## Known Limitations

- Literature evidence extraction is deterministic for the canonical demo, with Crossref metadata used as live context rather than full paper parsing.
- Persistence is local JSON, not SQLite, so it is suitable for the demo but not concurrent production workloads.
- The lab runner is simulated and intentionally uses fixed result data to keep the demo reproducible.
- Scientific claims are demo-grade and should not be treated as real materials guidance.

## Next Improvements

- Add SQLite migrations for durable multi-user storage.
- Add Semantic Scholar alongside Crossref and persist source-level retrieval diagnostics.
- Expand evidence extraction with DOI-aware deduplication and richer condition parsing.
- Add Playwright screenshot smoke tests for the dashboard.
- Add export formats for protocol payloads and provenance reports.
