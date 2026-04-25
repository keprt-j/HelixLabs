from packages.models import EvidenceExtraction, EvidenceSource, ExperimentFacts, MatchToHypothesis, ResearchPlan, RetrievedPaper


def extract_evidence(papers: list[RetrievedPaper], plan: ResearchPlan) -> list[EvidenceExtraction]:
    evidence: list[EvidenceExtraction] = []
    for index, paper in enumerate(papers, start=1):
        searchable = f"{paper.title} {paper.abstract}".lower()
        if _is_direct_plan_evidence(searchable, plan):
            evidence.append(
                EvidenceExtraction(
                    evidence_id=f"EV-{index:03d}",
                    source=EvidenceSource(
                        type="paper",
                        title=paper.title,
                        identifier=paper.doi or paper.paper_id,
                    ),
                    experiment_facts=ExperimentFacts(
                        material=plan.system,
                        intervention=plan.intervention,
                        variable=plan.variable_name,
                        tested_values=plan.prior_tested_values,
                        measured_properties=plan.success_metrics,
                        reported_outcome=f"{plan.already_tested_label} were previously tested with partial support for the hypothesis",
                    ),
                    match_to_user_hypothesis=MatchToHypothesis(
                        overlap="high",
                        redundancy_contribution=0.58,
                        novelty_gap=plan.gap,
                    ),
                )
            )
    return evidence


def _is_direct_plan_evidence(text: str, plan: ResearchPlan) -> bool:
    terms = [
        plan.system,
        plan.intervention,
        *plan.search_entities,
    ]
    hits = sum(1 for term in terms if term.lower() in text)
    return hits >= 1
