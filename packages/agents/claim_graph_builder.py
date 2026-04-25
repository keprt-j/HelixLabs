from packages.models import Claim, ClaimGraph


def build_claim_graph() -> ClaimGraph:
    return ClaimGraph(
        main_hypothesis="Moderate Mn doping improves LiFePO4 conductivity while preserving stability.",
        claims=[
            Claim(
                id="C1",
                claim="LiFePO4 is a feasible cobalt-free cathode candidate.",
                status="supported",
                evidence=["materials_database", "literature_search"],
            ),
            Claim(
                id="C2",
                claim="Low Mn doping improves conductivity.",
                status="partially_supported",
                evidence=["paper_match_001", "internal_run_R-017"],
            ),
            Claim(
                id="C3",
                claim="Mn substitution remains stable above 10% and below 20%.",
                status="uncertain",
                evidence=["internal_run_R-017", "negative_result_R-021"],
            ),
        ],
        weakest_high_value_claim="C3",
    )

