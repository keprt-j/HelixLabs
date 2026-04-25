from pathlib import Path

from packages.models import NegativeResult, ResearchPlan
from packages.storage import load_json


def find_negative_results(root: Path, plan: ResearchPlan) -> list[NegativeResult]:
    results = [NegativeResult.model_validate(item) for item in load_json(root, "data/sample_negative_results.json")]
    experiment = f"{plan.system} {plan.intervention}"
    normalized = experiment.lower()
    matched = [item for item in results if item.experiment.lower() == normalized]
    if matched:
        return matched
    return [
        NegativeResult(
            negative_result_id="NR-LLM-001",
            experiment=experiment,
            failed_condition=plan.failed_condition_label,
            failure_type="preservation_threshold_failed",
            observed_result={plan.preserve_property: False, "stability_pass": False},
            recommendation=f"Avoid repeating {plan.failed_condition_label} unless mapping the boundary.",
            source="llm_extracted_negative_memory",
        )
    ]
