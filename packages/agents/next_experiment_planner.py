from packages.models import CandidateNextExperiment, NextExperimentRecommendation


def plan_next_experiment() -> NextExperimentRecommendation:
    return NextExperimentRecommendation(
        candidate_next_experiments=[
            CandidateNextExperiment(
                name="Boundary screen between 14% and 16% Mn",
                conditions=[0.145, 0.150, 0.155],
                expected_information_gain=0.91,
                novelty=0.83,
                feasibility=0.88,
                redundancy=0.12,
                cost=0.25,
                risk=0.30,
                score=0.82,
            ),
            CandidateNextExperiment(
                name="Repeat 12-16% screen",
                conditions=[0.12, 0.14, 0.16],
                expected_information_gain=0.35,
                novelty=0.21,
                feasibility=0.95,
                redundancy=0.78,
                cost=0.40,
                risk=0.20,
                score=0.19,
            ),
        ],
        selected_next_experiment="Boundary screen between 14% and 16% Mn",
        rationale="14% passed and 16% failed, so the highest-value next experiment is to locate the stability boundary.",
    )

