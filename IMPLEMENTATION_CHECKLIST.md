# IMPLEMENTATION_CHECKLIST.md — HelixLabs Build Checklist

Use this as the implementation tracker. Work in vertical slices. Check off items only when the feature works through the backend and is visible or testable.

---

## Phase 0 — Repository Setup

- [ ] Create repo structure from `PLAN.md`.
- [ ] Create FastAPI backend app.
- [ ] Create React/Next frontend app.
- [ ] Add shared API/schema types or generated TypeScript types.
- [ ] Add SQLite or JSON persistence.
- [ ] Add seed data:
  - [ ] `sample_literature.json`
  - [ ] `sample_prior_runs.json`
  - [ ] `sample_negative_results.json`
  - [ ] `lab_resources.json`
  - [ ] `expected_schemas/materials_screen_v1.json`
- [ ] Add `.env.example`.
- [ ] Add README setup instructions.
- [ ] Add test framework.

Acceptance criteria:

- [ ] Backend starts.
- [ ] Frontend starts.
- [ ] Tests can run.
- [ ] Seed data is loaded or loadable.

---

## Phase 1 — Core Models and State Machine

- [ ] Define `ExperimentRun`.
- [ ] Define `RunState` enum.
- [ ] Define all core Pydantic models from `API_CONTRACTS.md`.
- [ ] Implement `POST /api/runs`.
- [ ] Implement `GET /api/runs/{run_id}`.
- [ ] Implement state transition utility.
- [ ] Implement provenance event logging.
- [ ] Implement `POST /api/runs/{run_id}/advance`.
- [ ] Add tests for state transitions.
- [ ] Add tests for provenance event creation.

Acceptance criteria:

- [ ] Creating a run returns a run ID.
- [ ] Advancing a run changes state deterministically.
- [ ] Each transition records a provenance event.
- [ ] Invalid transitions are rejected or handled gracefully.

---

## Phase 2 — Scientific Intent Parser

- [ ] Implement canonical goal parser.
- [ ] Extract:
  - [ ] domain
  - [ ] objective
  - [ ] base_material
  - [ ] intervention
  - [ ] target_property
  - [ ] constraints
  - [ ] success_metrics
  - [ ] search_entities
  - [ ] synonyms
- [ ] Implement `POST /api/runs/{run_id}/parse-goal`.
- [ ] Store parsed intent.
- [ ] Emit provenance event.
- [ ] Add tests.

Acceptance criteria:

- [ ] Canonical demo input produces the expected structured intent.
- [ ] Intent is visible through `GET /api/runs/{run_id}`.
- [ ] Provenance records parsing.

---

## Phase 3 — Live Literature Search + Cached Fallback

- [ ] Implement query planner.
- [ ] Implement at least one live literature client:
  - [ ] Semantic Scholar, Crossref, arXiv, or PubMed
- [ ] Implement cached fallback if live search fails.
- [ ] Implement deduplication by DOI / ID / title similarity.
- [ ] Implement `POST /api/runs/{run_id}/search-literature`.
- [ ] Store retrieved paper metadata.
- [ ] Show whether source was live or fallback.
- [ ] Add tests with mocked API failure.

Acceptance criteria:

- [ ] Literature search returns results.
- [ ] Demo works without API keys.
- [ ] If live API fails, fallback results load.
- [ ] Search query list is saved for provenance.

---

## Phase 4 — Evidence Extraction and Prior Work Matching

- [ ] Implement evidence extractor from retrieved papers and prior runs.
- [ ] Extract:
  - [ ] material
  - [ ] intervention
  - [ ] variable
  - [ ] tested values
  - [ ] measured properties
  - [ ] outcome
  - [ ] limitations
- [ ] Implement prior work matcher.
- [ ] Match exact/partial/analogous prior work.
- [ ] Identify tested conditions.
- [ ] Identify unresolved gap.
- [ ] Implement `POST /api/runs/{run_id}/match-prior-work`.
- [ ] Add tests.

Acceptance criteria:

- [ ] System finds prior low-Mn tests.
- [ ] System identifies high-Mn failure.
- [ ] System concludes the gap is between 10% and 20%.
- [ ] System recommends narrowed 12–16% screen.

---

## Phase 5 — Negative Results Memory

- [ ] Load negative-results seed data.
- [ ] Implement negative-results matcher.
- [ ] Implement `POST /api/runs/{run_id}/check-negative-results`.
- [ ] Incorporate negative results into risk and feasibility.
- [ ] Add tests.

Acceptance criteria:

- [ ] System finds negative result at 20% Mn.
- [ ] System recommends avoiding high-Mn redundant failure.
- [ ] Negative result appears in UI/report.

---

## Phase 6 — Claim Graph

- [ ] Implement claim graph builder.
- [ ] Create supported/partially supported/uncertain claims.
- [ ] Identify weakest high-value claim.
- [ ] Implement `POST /api/runs/{run_id}/build-claim-graph`.
- [ ] Store claim graph.
- [ ] Emit provenance event.
- [ ] Add tests.

Acceptance criteria:

- [ ] Claim graph includes C1, C2, C3 for canonical demo.
- [ ] Weakest high-value claim is stability boundary between 10% and 20%.

---

## Phase 7 — Experiment IR Compiler

- [ ] Define Experiment IR schema.
- [ ] Compile narrowed experiment from claim graph and prior work.
- [ ] Include:
  - [ ] hypothesis
  - [ ] target_claim
  - [ ] experiment_type
  - [ ] material
  - [ ] variables
  - [ ] controls
  - [ ] success_metrics
  - [ ] constraints
  - [ ] evidence_context
  - [ ] required_resources
  - [ ] expected_output_schema
- [ ] Implement `POST /api/runs/{run_id}/compile-ir`.
- [ ] Add tests.

Acceptance criteria:

- [ ] Canonical demo compiles 12%, 14%, 16% Mn.
- [ ] IR includes undoped and 10% prior baseline controls.
- [ ] IR includes expected schema `materials_screen_v1`.

---

## Phase 8 — Feasibility / Safety / Validity Validator

- [ ] Implement static validation checks:
  - [ ] variables defined
  - [ ] units / value ranges valid
  - [ ] controls present
  - [ ] metrics measurable
  - [ ] redundancy considered
  - [ ] known negative result considered
  - [ ] resources available
  - [ ] expected output schema exists
- [ ] Implement `POST /api/runs/{run_id}/validate-feasibility`.
- [ ] Add tests.

Acceptance criteria:

- [ ] Validator passes with warnings.
- [ ] Warnings mention already-tested low fractions.
- [ ] Warnings mention 20% Mn failed stability.
- [ ] Validator approves protocol generation.

---

## Phase 9 — Novelty / Redundancy / Value Scorer

- [ ] Implement scoring model.
- [ ] Score:
  - [ ] novelty
  - [ ] redundancy
  - [ ] expected information gain
  - [ ] feasibility
  - [ ] cost
  - [ ] risk
  - [ ] overall experiment value
- [ ] Implement `POST /api/runs/{run_id}/score-value`.
- [ ] Add tests.

Acceptance criteria:

- [ ] Narrowed experiment scores high value.
- [ ] Full repeat screen would score lower if evaluated.
- [ ] Score rationale is visible.

---

## Phase 10 — Protocol Generator

- [ ] Define Protocol and ProtocolStep models.
- [ ] Generate structured protocol from Experiment IR.
- [ ] Include dependencies and durations.
- [ ] Implement `POST /api/runs/{run_id}/generate-protocol`.
- [ ] Add tests.

Acceptance criteria:

- [ ] Protocol includes preparation, synthesis, structure validation, property prediction, schema validation.
- [ ] Each step has resource type and dependency metadata.

---

## Phase 11 — Cloud-Lab Scheduler

- [ ] Define lab resource model.
- [ ] Load resource seed data.
- [ ] Implement dependency-aware greedy scheduler.
- [ ] Include task start/end times.
- [ ] Implement scheduler score or priority metadata.
- [ ] Implement `POST /api/runs/{run_id}/schedule`.
- [ ] Add tests.

Acceptance criteria:

- [ ] All protocol steps are scheduled.
- [ ] Dependencies are respected.
- [ ] Resources match required capabilities.
- [ ] Schedule appears in UI/report.

---

## Phase 12 — Human Approval Gate

- [ ] Implement `AWAITING_HUMAN_APPROVAL` state.
- [ ] Implement `POST /api/runs/{run_id}/approve`.
- [ ] Allow frontend approval action.
- [ ] Store approval event.
- [ ] Add tests.

Acceptance criteria:

- [ ] Execution cannot proceed until approved.
- [ ] Approval is recorded in provenance.

---

## Phase 13 — Execution Adapter and Simulated Lab Runner

- [ ] Define execution adapter interface.
- [ ] Implement SimulatedLabAdapter.
- [ ] Execute scheduled tasks.
- [ ] Generate execution logs.
- [ ] Generate result CSV with intentional schema drift.
- [ ] Implement `POST /api/runs/{run_id}/execute`.
- [ ] Add tests.

Acceptance criteria:

- [ ] Simulated execution produces results.
- [ ] Execution logs are visible.
- [ ] Result file contains drifted columns: `mn_pct`, `e_hull`, `cond_proxy`, `stable`.

---

## Phase 14 — Failure Recovery Engine

- [ ] Simulate property predictor timeout.
- [ ] Generate recovery options.
- [ ] Select `retry_failed_condition`.
- [ ] Log recovery event.
- [ ] Implement `POST /api/runs/{run_id}/recover`.
- [ ] Add tests.

Acceptance criteria:

- [ ] Failure is visible.
- [ ] Recovery options are visible.
- [ ] Selected recovery avoids full rerun.
- [ ] Recovered execution continues.

---

## Phase 15 — Data Stent: Validation + Repair

- [ ] Load expected schema.
- [ ] Implement validator.
- [ ] Detect column mismatches.
- [ ] Repair:
  - [ ] `mn_pct` → `mn_fraction` and divide by 100
  - [ ] `e_hull` → `energy_above_hull`
  - [ ] `cond_proxy` → `conductivity_proxy`
  - [ ] `stable` → `stability_pass`
- [ ] Implement `POST /api/runs/{run_id}/validate-results`.
- [ ] Add tests.

Acceptance criteria:

- [ ] Broken schema is detected.
- [ ] Repairs are applied.
- [ ] Repaired output matches expected schema.
- [ ] Repair events are recorded.

---

## Phase 16 — Result Interpreter

- [ ] Implement result interpretation.
- [ ] Separate:
  - [ ] observed results
  - [ ] prior evidence
  - [ ] inference
  - [ ] uncertainty
  - [ ] limitations
- [ ] Implement `POST /api/runs/{run_id}/interpret`.
- [ ] Add tests.

Acceptance criteria:

- [ ] 12% and 14% pass.
- [ ] 16% fails.
- [ ] Useful region likely lies between 12% and 15%.
- [ ] Boundary between 14% and 16% remains uncertain.

---

## Phase 17 — Next Experiment Planner

- [ ] Generate candidate next experiments.
- [ ] Score each candidate.
- [ ] Select boundary screen at 14.5%, 15.0%, 15.5%.
- [ ] Implement `POST /api/runs/{run_id}/recommend-next`.
- [ ] Add tests.

Acceptance criteria:

- [ ] Selected recommendation is boundary screen.
- [ ] Repeat 12–16% screen scores lower.
- [ ] Recommendation rationale is clear.

---

## Phase 18 — Provenance Report + Memory Update

- [ ] Implement report generator.
- [ ] Include all stages.
- [ ] Implement `GET /api/runs/{run_id}/report`.
- [ ] Implement `POST /api/runs/{run_id}/update-memory`.
- [ ] Store completed experiment and negative results if applicable.
- [ ] Add tests.

Acceptance criteria:

- [ ] Report contains every major stage.
- [ ] Provenance timeline is complete.
- [ ] Experiment memory is updated.

---

## Phase 19 — Frontend Dashboard

- [ ] Build dashboard layout.
- [ ] Add run creation form.
- [ ] Add state machine progress.
- [ ] Add stage panels:
  - [ ] Intent
  - [ ] Literature
  - [ ] Prior work
  - [ ] Negative results
  - [ ] Claim graph
  - [ ] Experiment IR
  - [ ] Feasibility/value
  - [ ] Protocol
  - [ ] Schedule
  - [ ] Approval
  - [ ] Execution
  - [ ] Recovery
  - [ ] Data stent
  - [ ] Interpretation
  - [ ] Next experiment
  - [ ] Report
- [ ] Add “Run demo” or “Advance” button.
- [ ] Add loading/error states.
- [ ] Add final report view.

Acceptance criteria:

- [ ] Judge can follow workflow visually.
- [ ] No important output is hidden in backend logs only.
- [ ] Demo can be run from one screen.

---

## Phase 20 — Validation and Polish

- [ ] Run backend tests.
- [ ] Run frontend build/typecheck.
- [ ] Fix test failures.
- [ ] Run canonical demo end-to-end.
- [ ] Update README.
- [ ] Add screenshots if time permits.
- [ ] Add known limitations.
- [ ] Add next improvements.

Final acceptance criteria:

- [ ] App runs locally.
- [ ] Demo path works end-to-end.
- [ ] Tests pass or limitations are documented.
- [ ] README contains commands and demo script.
