# AGENTS.md — HelixLabs Codex Instructions

## Project Identity

Project name: **HelixLabs**

HelixLabs is a cloud-lab operating system for autonomous science. It compiles scientific intent into evidence-aware, non-redundant, scheduled, executable, validated, recoverable experiments, then recommends the next highest-value experiment.

The primary demo domain is **materials discovery**, specifically cobalt-free cathode optimization using LiFePO4 and Mn-doping as the canonical use case.

Canonical demo input:

> Find a low-cost cobalt-free cathode material and test whether Mn doping improves conductivity without hurting stability.

Expected demo conclusion:

> HelixLabs should avoid repeating already-tested Mn fractions, identify the unresolved stability boundary, compile a narrowed experiment, schedule and execute a simulated lab run, recover from a simulated failure, repair schema drift, interpret the result, recommend the next experiment, and generate a provenance report.

---

## Non-Negotiable Product Goals

Build HelixLabs as close to the final product architecture as possible, not as a shallow mock.

The application must demonstrate the full lifecycle:

1. Parse scientific intent.
2. Search live literature, with cached fallback.
3. Match prior work and identify redundancy.
4. Use negative-results memory.
5. Build a claim graph.
6. Compile an Experiment IR.
7. Validate feasibility, safety, controls, units, resources, and schema.
8. Score novelty, redundancy, expected information gain, feasibility, risk, and value.
9. Generate a structured protocol.
10. Schedule constrained lab resources.
11. Pause for human approval.
12. Execute a simulated/API-backed lab run.
13. Recover from at least one simulated execution failure.
14. Validate and repair output data schema drift.
15. Interpret results while separating observation, evidence, inference, uncertainty, and limitations.
16. Recommend the next highest-value experiment.
17. Generate a provenance report.
18. Update experiment memory.

---

## Files to Read Before Coding

Always read these files before making implementation decisions:

1. `PLAN.md`
2. `API_CONTRACTS.md`
3. `IMPLEMENTATION_CHECKLIST.md`
4. `README.md`

If the code conflicts with these documents, prefer the documents unless the implementation has already established a better working convention. If you deviate, update the documentation and explain why.

---

## Implementation Style

Implement in **vertical slices**, not isolated dead-end modules.

A correct vertical slice means:

- Backend model exists.
- Endpoint exists.
- Frontend displays the output.
- Provenance event is recorded.
- Tests or smoke checks exist.
- The canonical demo path still works.

Prefer reliable end-to-end behavior over theoretical extensibility.

Use real APIs where feasible, but always include cached fallbacks so the demo is reliable under API downtime, missing credentials, or rate limits.

---

## Required Stack

Use this stack unless the existing repo already uses something equivalent:

### Backend

- Python 3.11+
- FastAPI
- Pydantic v2
- SQLite or local JSON persistence
- pytest

### Frontend

- React or Next.js
- TypeScript
- Tailwind CSS if available
- Clean dashboard UI, not chat-only

### Data / validation

- pandas for CSV/result transformations
- Pydantic models for structured schemas
- Optional: `frictionless` for tabular validation if simple to install

### Live search

Implement live literature search with at least one source and use cached fallback.

Preferred live sources:

- Semantic Scholar
- Crossref
- arXiv
- PubMed / NCBI E-utilities if relevant

Do not block the demo on API keys. If a live API fails, use seeded fallback papers and show that fallback was used.

---

## Coding Standards

- Use typed Pydantic models for all core objects.
- Keep schemas stable and frontend-friendly.
- Avoid free-form blobs when a structured schema is possible.
- Every important transition must create a provenance event.
- Every endpoint should return JSON that the UI can render directly.
- Keep modules small and named according to the architecture.
- Write code that is easy to demo and easy to inspect.
- Prefer deterministic demo data over unpredictable model-only behavior.
- Do not hardcode everything into the frontend. Core workflow should live in backend services.

---

## State Machine

Implement or simulate this state machine:

```text
CREATED
  ↓
GOAL_PARSED
  ↓
LITERATURE_SEARCHED
  ↓
PRIOR_WORK_MATCHED
  ↓
NEGATIVE_RESULTS_CHECKED
  ↓
CLAIM_GRAPH_BUILT
  ↓
EXPERIMENT_IR_COMPILED
  ↓
FEASIBILITY_VALIDATED
  ↓
NOVELTY_VALUE_SCORED
  ↓
PROTOCOL_GENERATED
  ↓
SCHEDULED
  ↓
AWAITING_HUMAN_APPROVAL
  ↓
APPROVED
  ↓
EXECUTING
  ↓
EXECUTION_FAILED_OR_COMPLETED
  ↓
RECOVERY_APPLIED
  ↓
RESULTS_COLLECTED
  ↓
RESULTS_VALIDATED
  ↓
RESULTS_REPAIRED
  ↓
INTERPRETED
  ↓
NEXT_EXPERIMENT_RECOMMENDED
  ↓
REPORT_GENERATED
  ↓
MEMORY_UPDATED
```

The UI should visibly communicate state progress.

---

## Canonical Demo Requirements

The canonical demo must show this exact story:

1. User enters:
   > Find a low-cost cobalt-free cathode material and test whether Mn doping improves conductivity without hurting stability.

2. HelixLabs parses the goal into structured scientific intent.

3. HelixLabs searches live literature and/or fallback paper data.

4. HelixLabs finds:
   - 0%, 5%, and 10% Mn were already tested.
   - 20% Mn previously failed stability.
   - The unresolved gap is between 10% and 20%.

5. HelixLabs builds a claim graph and identifies the weakest high-value claim:
   - Stability boundary between moderately successful and failed Mn fractions.

6. HelixLabs compiles an Experiment IR:
   - Test 12%, 14%, and 16% Mn.
   - Use prior 10% baseline and undoped control.
   - Metrics: energy_above_hull, conductivity_proxy, stability_pass.

7. HelixLabs validates feasibility:
   - Flags already-tested conditions.
   - Flags known negative result at 20%.
   - Confirms controls, schema, resources, and measurable outputs.

8. HelixLabs scores the experiment:
   - High novelty.
   - Low redundancy.
   - High expected information gain.

9. HelixLabs generates a structured protocol.

10. HelixLabs schedules lab resources:
   - simulated_synthesis_station
   - structure_validator
   - property_predictor
   - data_validation_engine

11. HelixLabs pauses for approval.

12. HelixLabs executes a simulated run.

13. HelixLabs simulates at least one failure:
   - property_predictor_timeout on one condition.

14. HelixLabs chooses a recovery:
   - retry_failed_condition rather than rerun_full_experiment.

15. HelixLabs produces intentionally drifted output:
   - `mn_pct` instead of `mn_fraction`
   - `e_hull` instead of `energy_above_hull`
   - `cond_proxy` instead of `conductivity_proxy`
   - `stable` instead of `stability_pass`

16. HelixLabs repairs schema drift.

17. HelixLabs interprets results:
   - 12% and 14% pass stability.
   - 16% fails stability.
   - useful region likely lies between 12% and 15%.
   - exact boundary between 14% and 16% is unresolved.

18. HelixLabs recommends:
   - boundary screen at 14.5%, 15.0%, and 15.5%.

19. HelixLabs generates a provenance report.

20. HelixLabs updates experiment memory.

---

## Frontend Requirements

The frontend should be a dashboard, not a generic chat screen.

Required panels:

1. Research Goal
2. State Machine Progress
3. Literature / Prior Work Search
4. Evidence and Experiment Matches
5. Negative Results
6. Claim Graph
7. Experiment IR
8. Feasibility and Value Scores
9. Protocol
10. Cloud-Lab Schedule
11. Approval Gate
12. Execution Monitor
13. Failure Recovery
14. Data Stent Validation and Repair
15. Result Interpretation
16. Next Experiment Recommendation
17. Provenance Report

Use clean visual hierarchy. Judges should understand the system in under 60 seconds.

---

## Backend Requirements

Required endpoints are listed in `API_CONTRACTS.md`.

At minimum, implement:

- `POST /api/runs`
- `GET /api/runs/{run_id}`
- `POST /api/runs/{run_id}/advance`
- `POST /api/runs/{run_id}/approve`
- `GET /api/runs/{run_id}/report`

Prefer implementing the full endpoint set from `API_CONTRACTS.md` if time permits.

---

## Testing and Validation

Before reporting completion:

1. Run backend tests.
2. Run frontend typecheck/build if available.
3. Run the app locally if possible.
4. Verify the canonical demo path end-to-end.
5. Confirm every state has visible output.
6. Confirm cached fallback works when live search fails.
7. Confirm provenance events are created.
8. Confirm schema drift is repaired.
9. Confirm next-experiment recommendation is correct.

If tests cannot run because dependencies are missing, add setup instructions and explain exactly what remains unvalidated.

---

## Definition of Done

The work is done only when:

- The app runs locally.
- The canonical demo path works end-to-end.
- The frontend displays each major stage.
- Backend APIs return structured JSON.
- Live literature search works or gracefully falls back.
- Prior work matching identifies redundancy.
- Negative results are incorporated.
- Experiment IR is compiled.
- Scheduler produces a resource schedule.
- Simulated execution produces results.
- Failure recovery is demonstrated.
- Data stent repairs schema drift.
- Next experiment recommendation is generated.
- Provenance report is generated.
- Tests or smoke checks pass.
- README explains setup and demo flow.

---

## Do Not Do

- Do not build only a chatbot.
- Do not stop after scaffolding.
- Do not create unused abstractions with no demo path.
- Do not depend on live APIs without fallback.
- Do not hide outputs in logs only; show them in the UI.
- Do not make all reasoning opaque.
- Do not overclaim real scientific validity from simulated data.
- Do not skip provenance.
- Do not skip schema repair.
- Do not skip prior-work checking.
