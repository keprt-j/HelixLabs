from packages.models import ExperimentIR, ResearchPlan


def compile_experiment_ir(plan: ResearchPlan) -> ExperimentIR:
    return ExperimentIR(
        experiment_id="EXP-001",
        domain=plan.domain,
        hypothesis=plan.hypothesis,
        target_claim="C3",
        experiment_type="evidence_aware_boundary_screen",
        material=plan.system,
        variables={plan.variable_name: plan.candidate_values},
        controls=plan.controls,
        success_metrics=plan.success_metrics,
        constraints={
            "stability_threshold_ev": 0.05,
            "variable_label": plan.variable_label,
            "variable_unit": plan.variable_unit,
            "max_runtime_hours": 4,
        },
        evidence_context={
            "already_tested": [*plan.prior_tested_values, *plan.known_failed_values],
            "unresolved_gap": plan.gap,
        },
        required_resources=[
            "simulated_synthesis_station",
            "structure_validator",
            "property_predictor",
            "data_validation_engine",
        ],
        expected_output_schema="materials_screen_v1",
    )
