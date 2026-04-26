# HelixLabs Architecture Invariants

This document defines non-negotiable platform behavior as HelixLabs evolves from a
single-domain surrogate into a domain-agnostic experimentation runtime.

## Invariants

1. Truthfulness
- Every data artifact MUST include origin labels from:
  - `retrieved` (external evidence)
  - `simulated` (plugin/executor output)
  - `estimated` (inferred heuristic)
  - `uploaded` (user-provided real measurements)
- UI and reports MUST not present simulated values as observed real-world outcomes.

2. Reproducibility
- Each execution MUST persist:
  - run seed
  - simulation/executor config
  - executor/plugin identifier + version
- Re-running the same run with identical seed/config SHOULD reproduce equivalent outputs.

3. Observability
- Every successful run MUST expose renderable artifacts:
  - observations table (or explicit reason unavailable)
  - at least one chart-compatible series (or explicit reason unavailable)
  - procedural trace/events
- Missing artifacts MUST be represented as structured errors/warnings, not silent omission.

4. Extensibility
- Core state machine MUST remain domain-agnostic.
- Domain-specific logic MUST live behind plugin/executor boundaries.
- New experiment domains should be addable without changing orchestration states.

## Data Origin and Fidelity

All produced artifacts should carry:
- `origin`
- `fidelity` (`high`, `medium`, `low`)
- `provenance_refs` (literature IDs, uploaded dataset IDs, executor metadata)

This enables explicit confidence messaging in API and UI.

## Plugin Boundary (Target)

A plugin/executor is responsible for:
- `can_handle(experiment_ir)`
- `prepare(experiment_ir)`
- `execute(prepared_plan)`
- `analyze(results)`
- `recommend_next(results, experiment_ir)`

Core orchestration is responsible for:
- stage transitions
- persistence
- provenance/event logging
- API contracts and response envelopes

## Backward Compatibility

Legacy artifact keys may be retained via adapter layers during migration, but new
logic should target normalized contracts first.
