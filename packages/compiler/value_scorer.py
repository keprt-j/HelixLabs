from packages.models import ExperimentValueScore


def score_experiment_value() -> ExperimentValueScore:
    return ExperimentValueScore(
        prior_work_status="partially_tested",
        redundancy_score=0.21,
        novelty_score=0.78,
        expected_information_gain=0.84,
        feasibility_score=0.91,
        resource_cost=0.32,
        risk_score=0.27,
        overall_experiment_value=0.82,
        recommendation="Proceed with narrowed screen.",
    )

