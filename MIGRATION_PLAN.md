# Migration Plan (MVP -> Current Architecture)

This repository has diverged from `origin/MVP` with unrelated git history.  
Migration should be capability-based, not merge-based.

## Decision

- Keep current branch architecture as canonical:
  - Vite frontend in `src/`
  - Python backend in `apps/api/helixlabs/`
- Port MVP capabilities incrementally.

## Phase 1 - API Parity Shell (in progress)

Goal: expose MVP-compatible stage endpoints while keeping current internals.

- Keep existing:
  - `POST /api/runs`
  - `GET /api/runs/{run_id}`
  - `POST /api/runs/{run_id}/advance`
  - `GET /api/runs/{run_id}/report`
- Add MVP-style stage endpoints:
  - parse-goal, search-literature, match-prior-work, check-negative-results,
    build-claim-graph, compile-ir, validate-feasibility, score-value,
    generate-protocol, schedule, execute, recover, validate-results,
    interpret, recommend-next, update-memory
- Add approve endpoint parity:
  - `POST /api/runs/{run_id}/approve`

Implementation style:
- Endpoints map to current orchestrator stage primitives.
- Return deterministic response envelopes that include current run snapshot.

## Phase 2 - Domain Depth Port

Port high-value backend modules from MVP into current service boundaries:

- literature query planning + dedup
- prior-work matching + negative-results memory
- richer claim graph derivation
- compiler/feasibility/value scoring logic
- scheduler and recovery strategy scoring
- result interpretation and provenance report generation

## Phase 3 - Data + Contracts Hardening

- Expand contracts under `packages/contracts/` to stage-specific schemas.
- Add strict validation before persistence and API response serialization.
- Reintroduce representative seed/runtime data from MVP where useful.

## Phase 4 - Testing Parity

- Rebuild critical tests in current layout:
  - lifecycle/state machine
  - literature retrieval + ranking quality
  - compiler/feasibility/value
  - data validation/repair
- Add integration smoke for full run lifecycle to outcomes/report.

## Immediate Next Actions

1. Finish stage endpoint parity and approve flow.
2. Start porting MVP literature/prior-work modules into current services.
3. Add integration tests for create/get/advance/stage endpoints.
