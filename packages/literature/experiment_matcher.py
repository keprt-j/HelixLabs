from pathlib import Path

from packages.models import PriorMatchItem, PriorWorkMatch
from packages.storage import load_json


def match_prior_work(root: Path) -> PriorWorkMatch:
    prior_runs = load_json(root, "data/sample_prior_runs.json")
    low_run = next(item for item in prior_runs if item["run_id"] == "R-017")
    high_run = next(item for item in prior_runs if item["run_id"] == "R-021")
    return PriorWorkMatch(
        prior_work_status="partially_tested",
        matches=[
            PriorMatchItem(
                source_type="paper",
                title="Manganese-substituted lithium iron phosphate cathodes",
                identifier="10.0000/helix.lfp.mn.low",
                overlap="high",
                tested_conditions=["0%", "5%", "10% Mn"],
                reported_result="low Mn substitution improved conductivity while preserving stability",
                evidence_strength=0.81,
            ),
            PriorMatchItem(
                source_type="internal_prior_run",
                source_id=high_run["run_id"],
                overlap="medium",
                tested_conditions=["20% Mn"],
                reported_result=high_run["reported_result"],
                evidence_strength=high_run["evidence_strength"],
            ),
            PriorMatchItem(
                source_type="internal_prior_run",
                source_id=low_run["run_id"],
                overlap="high",
                tested_conditions=["0%", "5%", "10% Mn"],
                reported_result=low_run["reported_result"],
                evidence_strength=low_run["evidence_strength"],
            ),
        ],
        gap="The stability boundary between 10% and 20% Mn remains unresolved.",
        recommendation="Run a narrowed screen around 12-16% Mn instead of repeating the full range.",
    )

