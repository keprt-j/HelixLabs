from pathlib import Path

from packages.models import EvidenceExtraction, PriorMatchItem, PriorWorkMatch, ResearchPlan
from packages.research_plans import values_to_conditions
from packages.storage import load_json


def match_prior_work(root: Path, evidence: list[EvidenceExtraction] | None, plan: ResearchPlan) -> PriorWorkMatch:
    prior_runs = load_json(root, "data/sample_prior_runs.json")
    matching_prior_runs = [item for item in prior_runs if item["experiment"].lower() == f"{plan.system} {plan.intervention}".lower()]
    evidence_title = evidence[0].source.title if evidence else f"Live literature result for {plan.system} {plan.intervention}"
    evidence_identifier = evidence[0].source.identifier if evidence else "live_literature_unmatched"
    low_run = matching_prior_runs[0] if matching_prior_runs else None
    high_run = matching_prior_runs[-1] if len(matching_prior_runs) > 1 else None
    return PriorWorkMatch(
        prior_work_status="partially_tested",
        matches=[
            PriorMatchItem(
                source_type="paper",
                title=evidence_title,
                identifier=evidence_identifier,
                overlap="high",
                tested_conditions=values_to_conditions(plan.prior_tested_values, plan.variable_label, plan.variable_unit),
                reported_result=f"{plan.already_tested_label} partially support the hypothesis",
                evidence_strength=0.81,
            ),
            PriorMatchItem(
                source_type="internal_prior_run",
                source_id=high_run["run_id"] if high_run else "llm_negative_seed",
                overlap="medium",
                tested_conditions=values_to_conditions(plan.known_failed_values, plan.variable_label, plan.variable_unit),
                reported_result=high_run["reported_result"] if high_run else f"{plan.failed_condition_label} failed the preservation criterion.",
                evidence_strength=high_run["evidence_strength"] if high_run else 0.9,
            ),
            PriorMatchItem(
                source_type="internal_prior_run",
                source_id=low_run["run_id"] if low_run else "llm_prior_seed",
                overlap="high",
                tested_conditions=values_to_conditions(plan.prior_tested_values, plan.variable_label, plan.variable_unit),
                reported_result=low_run["reported_result"] if low_run else f"{plan.already_tested_label} were already tested.",
                evidence_strength=low_run["evidence_strength"] if low_run else 0.84,
            ),
        ],
        gap=plan.gap,
        recommendation=plan.recommendation,
    )
