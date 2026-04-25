from packages.models import CandidateNextExperiment, NextExperimentRecommendation, ResearchPlan


def plan_next_experiment(plan: ResearchPlan) -> NextExperimentRecommendation:
    return NextExperimentRecommendation(
        candidate_next_experiments=[
            CandidateNextExperiment(
                name=f"Boundary screen for {plan.variable_label}",
                conditions=plan.next_values,
                expected_information_gain=0.91,
                novelty=0.83,
                feasibility=0.88,
                redundancy=0.12,
                cost=0.25,
                risk=0.30,
                score=0.82,
            ),
            CandidateNextExperiment(
                name=f"Repeat current {plan.variable_label} screen",
                conditions=plan.candidate_values,
                expected_information_gain=0.35,
                novelty=0.21,
                feasibility=0.95,
                redundancy=0.78,
                cost=0.40,
                risk=0.20,
                score=0.19,
            ),
        ],
        selected_next_experiment=f"Boundary screen for {plan.variable_label}",
        rationale=plan.interpretation.uncertainty,
    )
