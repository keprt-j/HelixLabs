from packages.models import EvidenceExtraction, EvidenceSource, ExperimentFacts, MatchToHypothesis, RetrievedPaper


def extract_evidence(papers: list[RetrievedPaper]) -> list[EvidenceExtraction]:
    evidence: list[EvidenceExtraction] = []
    for index, paper in enumerate(papers, start=1):
        if index == 1 or "manganese" in paper.title.lower() or "lifepo4" in paper.abstract.lower():
            evidence.append(
                EvidenceExtraction(
                    evidence_id=f"EV-{index:03d}",
                    source=EvidenceSource(
                        type="paper",
                        title=paper.title,
                        identifier=paper.doi or paper.paper_id,
                    ),
                    experiment_facts=ExperimentFacts(
                        material="LiFePO4",
                        intervention="Mn doping",
                        variable="mn_fraction",
                        tested_values=[0.0, 0.05, 0.10],
                        measured_properties=["conductivity", "stability"],
                        reported_outcome="10% Mn improved conductivity while retaining stability",
                    ),
                    match_to_user_hypothesis=MatchToHypothesis(
                        overlap="high",
                        redundancy_contribution=0.58,
                        novelty_gap="No results between 10% and 20%",
                    ),
                )
            )
            break
    return evidence

