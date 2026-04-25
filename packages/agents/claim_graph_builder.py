from packages.models import Claim, ClaimGraph, ResearchPlan


def build_claim_graph(plan: ResearchPlan) -> ClaimGraph:
    return ClaimGraph(
        main_hypothesis=plan.hypothesis,
        claims=[
            Claim.model_validate(claim.model_dump())
            for claim in plan.claims
        ],
        weakest_high_value_claim="C3",
    )
