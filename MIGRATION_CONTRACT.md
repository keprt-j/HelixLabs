# Migration Contract: Legacy Payloads to Experiment IR

This contract defines how current stage artifacts map to the new universal
`ExperimentIR` model while preserving API compatibility.

## Goals
- Avoid breaking existing frontend panels during migration.
- Allow backend to emit both:
  - normalized `experiment_ir` + validation report
  - legacy convenience views for existing tabs

## Legacy Keys (Current)

- `scientific_intent`
- `literature`
- `prior_work`
- `claim_graph`
- `experiment_ir`
- `feasibility_report`
- `value_score`
- `protocol`
- `schedule`
- `execution_log`
- `failure_recovery_plan`
- `validation_report`
- `interpretation`
- `next_experiment_recommendation`
- `report`

## Normalized Canonical Keys (Target)

- `experiment_ir`
- `ir_validation`
- `normalized_results`
- `procedure_trace`
- `summary_metrics`
- `provenance`

## Adapter Rule

During migration, each stage may produce both canonical and legacy fields.
Legacy fields are considered derived views over canonical fields and should not be
source-of-truth long term.

## Deprecation Policy

1. Introduce canonical field.
2. Keep legacy alias for at least one release window.
3. Update frontend to canonical source.
4. Remove legacy alias only after migration checklists pass.
