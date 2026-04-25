from packages.models import ExperimentIR


def compile_experiment_ir() -> ExperimentIR:
    return ExperimentIR(
        experiment_id="EXP-001",
        domain="materials_discovery",
        hypothesis="Moderate Mn doping improves conductivity while preserving stability.",
        target_claim="C3",
        experiment_type="dopant_boundary_screen",
        material="LiFePO4",
        variables={"mn_fraction": [0.12, 0.14, 0.16]},
        controls=["undoped_LiFePO4", "10_percent_Mn_prior_baseline"],
        success_metrics=["energy_above_hull", "conductivity_proxy", "stability_pass"],
        constraints={
            "stability_threshold_ev": 0.05,
            "exclude_elements": ["Co", "Ni"],
            "max_runtime_hours": 4,
        },
        evidence_context={
            "already_tested": [0.0, 0.05, 0.10, 0.20],
            "unresolved_gap": "12-16% Mn stability boundary",
        },
        required_resources=[
            "simulated_synthesis_station",
            "structure_validator",
            "property_predictor",
            "data_validation_engine",
        ],
        expected_output_schema="materials_screen_v1",
    )

