# CODEX_PROMPTS.md — Prompts for Implementing HelixLabs

Use these prompts in Codex. Start with the full implementation prompt. If Codex drifts or the repo becomes too large, use the phase prompts.

---

## Prompt 1 — Full Implementation Prompt

```text
Read AGENTS.md, PLAN.md, IMPLEMENTATION_CHECKLIST.md, API_CONTRACTS.md, and README.md completely before coding.

Your task is to implement HelixLabs as close to the final architecture as possible.

Build a working full-stack MVP with:
- FastAPI backend
- React/Next frontend
- SQLite or local JSON persistence
- typed schemas
- live literature search with cached fallback
- prior-work matching
- negative-results memory
- claim graph
- Experiment IR compiler
- feasibility validator
- novelty/redundancy/value scorer
- protocol generator
- lab resource scheduler
- human approval checkpoint
- simulated lab execution
- failure recovery
- data stent validation and repair
- result interpretation
- next-experiment recommendation
- provenance report
- experiment memory update

Implement this step by step following IMPLEMENTATION_CHECKLIST.md.

Important:
1. Start by creating the repo structure and core data models.
2. Then implement the backend state machine and API.
3. Then implement the full demo path end-to-end.
4. Then implement the frontend dashboard.
5. Then add tests and validation.
6. Run the app locally and verify the demo flow.
7. Run all tests, linting, and type checks where available.
8. Update README.md with actual setup commands, environment variables, and the demo script.

Do not stop after scaffolding. Continue until the demo path works end-to-end.

The canonical demo input is:
“Find a low-cost cobalt-free cathode material and test whether Mn doping improves conductivity without hurting stability.”

The expected demo behavior is:
1. Parse the goal.
2. Search live literature, with cached fallback.
3. Find prior low-Mn tests and a negative high-Mn result.
4. Build a claim graph.
5. Compile a narrowed 12%, 14%, 16% Mn experiment.
6. Validate feasibility.
7. Score novelty/redundancy/value.
8. Generate protocol.
9. Schedule lab resources.
10. Pause for approval.
11. Execute simulated run.
12. Recover from a simulated timeout.
13. Detect schema drift.
14. Repair the result data.
15. Interpret the result.
16. Recommend a boundary screen at 14.5%, 15.0%, and 15.5%.
17. Generate a provenance report.
18. Update experiment memory.

When finished, provide:
- summary of implemented features
- commands to run
- test results
- known limitations
- next improvements
```

---

## Prompt 2 — Backend Foundation

```text
Read AGENTS.md, PLAN.md, IMPLEMENTATION_CHECKLIST.md, and API_CONTRACTS.md.

Implement the backend foundation first:
- FastAPI app
- Pydantic models for every schema in API_CONTRACTS.md
- ExperimentRun and RunState
- local persistence using SQLite or JSON
- provenance event logging
- POST /api/runs
- GET /api/runs/{run_id}
- POST /api/runs/{run_id}/advance
- tests for state transitions and provenance events

Do not build a fake one-file backend if a cleaner module structure is feasible. Keep the canonical demo path in mind.
```

---

## Prompt 3 — Evidence Layer

```text
Implement the evidence layer for HelixLabs:
- scientific intent parser
- query planner
- live literature client using one public source
- cached fallback literature data
- deduplication
- evidence extraction
- prior-work matcher
- negative-results matcher

Required endpoints:
- POST /api/runs/{run_id}/parse-goal
- POST /api/runs/{run_id}/search-literature
- POST /api/runs/{run_id}/match-prior-work
- POST /api/runs/{run_id}/check-negative-results

The canonical demo must find prior 0%, 5%, 10% Mn tests and a negative 20% Mn result, then identify the gap between 10% and 20%.
```

---

## Prompt 4 — Reasoning and Compilation Layer

```text
Implement the reasoning and compilation layer:
- claim graph builder
- Experiment IR compiler
- feasibility/safety/validity validator
- novelty/redundancy/value scorer
- protocol generator

Required endpoints:
- POST /api/runs/{run_id}/build-claim-graph
- POST /api/runs/{run_id}/compile-ir
- POST /api/runs/{run_id}/validate-feasibility
- POST /api/runs/{run_id}/score-value
- POST /api/runs/{run_id}/generate-protocol

The canonical demo must compile a narrowed 12%, 14%, 16% Mn experiment with controls, required resources, expected schema, and warnings about prior work.
```

---

## Prompt 5 — Operating Layer

```text
Implement the operating layer:
- lab resource model
- dependency-aware scheduler
- human approval gate
- execution adapter interface
- SimulatedLabAdapter
- simulated execution logs
- simulated property predictor timeout
- failure recovery engine

Required endpoints:
- POST /api/runs/{run_id}/schedule
- POST /api/runs/{run_id}/approve
- POST /api/runs/{run_id}/execute
- POST /api/runs/{run_id}/recover

Execution must produce drifted CSV columns:
candidate_id,mn_pct,e_hull,cond_proxy,stable
```

---

## Prompt 6 — Data Stent and Iteration Layer

```text
Implement the data and iteration layer:
- expected result schema loading
- schema validation
- schema repair engine
- result interpretation
- next experiment planner
- provenance report
- experiment memory update

Required endpoints:
- POST /api/runs/{run_id}/validate-results
- POST /api/runs/{run_id}/interpret
- POST /api/runs/{run_id}/recommend-next
- POST /api/runs/{run_id}/update-memory
- GET /api/runs/{run_id}/report

The data stent must repair:
- mn_pct → mn_fraction and divide by 100
- e_hull → energy_above_hull
- cond_proxy → conductivity_proxy
- stable → stability_pass

The next experiment must be a boundary screen at 14.5%, 15.0%, and 15.5%.
```

---

## Prompt 7 — Frontend Dashboard

```text
Build the HelixLabs frontend dashboard.

It must show:
- research goal input
- state machine progress
- literature/prior work search
- negative results
- claim graph
- Experiment IR
- feasibility and value scores
- protocol
- cloud-lab schedule
- approval gate
- execution monitor
- failure recovery
- data stent validation and repair
- result interpretation
- next experiment recommendation
- provenance report

Add a simple “Run Demo” or “Advance” flow so judges can watch the canonical demo progress through the system.
```

---

## Prompt 8 — Validation and Polish

```text
Run the full project validation:
- backend tests
- frontend typecheck/build
- canonical demo end-to-end
- fallback behavior when live literature search fails
- provenance completeness
- data repair correctness
- next experiment recommendation correctness

Fix all failures you can. Update README.md with exact setup commands, demo script, known limitations, and next improvements.

Before finishing, review your own diff and identify any incomplete or risky areas.
```

---

## Prompt 9 — Emergency Scope Control

Use this if the build is running out of time.

```text
We are close to demo time. Prioritize one fully working vertical slice over incomplete breadth.

Ensure the following work end-to-end:
1. Create run.
2. Parse canonical goal.
3. Use cached literature/prior work if live search is unstable.
4. Match prior low-Mn tests and negative 20% result.
5. Compile narrowed 12%, 14%, 16% experiment.
6. Generate protocol.
7. Schedule resources.
8. Approve run.
9. Execute simulated run with one failure.
10. Recover by retrying failed condition.
11. Repair schema drift.
12. Interpret results.
13. Recommend 14.5%, 15.0%, 15.5% boundary screen.
14. Generate report.
15. Show all of this in frontend.

Cut or simplify anything else.
```

---

## Prompt 10 — Final Self-Review

```text
Review the implementation against AGENTS.md, PLAN.md, IMPLEMENTATION_CHECKLIST.md, and API_CONTRACTS.md.

Return:
1. What is fully implemented.
2. What is partially implemented.
3. What is missing.
4. Commands to run backend.
5. Commands to run frontend.
6. Commands to run tests.
7. Demo steps.
8. Any known failure modes.
9. Highest-impact improvements if we have 2 more hours.
```
