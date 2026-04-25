# HelixLabs

HelixLabs is a cloud-lab operating system for autonomous science. It compiles scientific intent into evidence-aware, non-redundant, scheduled, executable, validated, recoverable experiments, then recommends the next highest-value experiment.

The MVP implements a broad LLM-planned experiment workflow, with the canonical materials-discovery demo for cobalt-free cathode optimization as the primary judge path.

## What Is Implemented

- FastAPI backend with typed Pydantic v2 schemas.
- JSON persistence under `data/runtime/`.
- OpenAI structured-output research planner for open-ended scientific goals.
- Public Crossref literature lookup with no deterministic runtime fallback.
- Prior-work matching for already-tested conditions and failed high-risk conditions.
- Negative-results memory.
- Claim graph with weakest high-value claim selection.
- Experiment IR compiler driven by the generated research plan.
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
tests/          Pytest coverage for workflow, literature, compiler, and data stent
```

## Environment

Copy `.env.example` to `.env` and set your OpenAI API key.

```powershell
Copy-Item .env.example .env
```

Required:

```text
OPENAI_API_KEY=sk-...
HELIXLABS_OPENAI_MODEL=gpt-4.1-mini
```

Live literature search uses Crossref. There is no deterministic runtime fallback for the LLM planner or literature search; tests mock those network boundaries.

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

## Additional Test Prompts

The dashboard includes quick-fill buttons for example goals, and you can enter other scientific questions. The LLM planner converts the goal into the structured research plan used by the rest of the workflow.

```text
Optimize a perovskite solar absorber and test whether bromide iodide ratio tuning improves efficiency without hurting phase stability.
```

```text
Find the best enzyme buffer pH and test whether mildly alkaline conditions improve activity without hurting fold stability.
```

Other examples to try:

```text
Screen sodium-ion cathode dopants and test whether magnesium substitution improves cycling stability without lowering capacity.
```

```text
Optimize a biodegradable polymer blend and test whether adding citrate plasticizer improves toughness without reducing degradation rate.
```

```text
Find a low-cost electrocatalyst formulation and test whether nickel doping improves oxygen evolution activity without hurting durability.
```

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

- `pytest`: 13 passed.
- `npm run typecheck`: passed.
- `npm run build`: passed with Next.js 16.2.4.
- `npm audit`: 0 vulnerabilities after pinning Next.js 16.2.4 and overriding PostCSS to 8.5.10.
- Local backend smoke: `GET /api/health` returned `status: ok`.
- Local frontend smoke returned HTTP 200.
- End-to-end API smoke reached `MEMORY_UPDATED` with 23 provenance events.
- Real LLM-backed workflow smoke reached `MEMORY_UPDATED` with Crossref `live` retrieval and canonical candidates `[0.12, 0.14, 0.16]`.

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

- The LLM planner creates structured experiment plans, but literature evidence extraction still uses Crossref metadata rather than full-text paper parsing.
- Persistence is local JSON, not SQLite, so it is suitable for the demo but not concurrent production workloads.
- The lab runner is simulated and uses LLM-planned synthetic result rows to demonstrate execution, failure recovery, schema drift, and interpretation.
- Scientific claims are demo-grade and should not be treated as real materials guidance.

## Next Improvements

- Add SQLite migrations for durable multi-user storage.
- Add Semantic Scholar alongside Crossref and persist source-level retrieval diagnostics.
- Expand evidence extraction with DOI-aware deduplication, abstract parsing, and richer condition extraction.
- Add Playwright screenshot smoke tests for the dashboard.
- Add export formats for protocol payloads and provenance reports.
