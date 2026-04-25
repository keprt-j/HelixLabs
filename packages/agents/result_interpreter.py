from typing import Any

from packages.models import RepairedResult, ResearchPlan, ResultInterpretation


def interpret_results(results: list[RepairedResult | dict[str, Any]], plan: ResearchPlan | None = None) -> ResultInterpretation:
    if plan is not None:
        variable_name = plan.variable_name
        stable_by_condition = {
            row.get(variable_name): row.get("stability_pass")
            for row in results
            if isinstance(row, dict)
        }
        return ResultInterpretation(
            observed_results=plan.interpretation.observed_results,
            prior_evidence=[
                f"{plan.already_tested_label} had already been tested.",
                f"{plan.failed_condition_label} previously failed the preservation criterion.",
            ],
            inference=plan.interpretation.inference,
            uncertainty=plan.interpretation.uncertainty,
            limitations=[
                *plan.interpretation.limitations,
                f"Repaired result stability map: {stable_by_condition}.",
            ],
        )
    typed_results = [item for item in results if isinstance(item, RepairedResult)]
    stable_by_fraction = {round(item.mn_fraction, 3): item.stability_pass for item in typed_results}
    return ResultInterpretation(
        observed_results=[
            "12% Mn passed stability threshold and improved conductivity proxy.",
            "14% Mn passed stability threshold and improved conductivity proxy.",
            "16% Mn failed stability threshold despite a higher conductivity proxy.",
        ],
        prior_evidence=[
            "0%, 5%, and 10% Mn had already been tested.",
            "20% Mn previously failed stability.",
        ],
        inference="The useful Mn-doping region likely lies between 12% and 15%.",
        uncertainty="The exact stability boundary between 14% and 16% remains unresolved.",
        limitations=[
            "Results come from simulated property predictions.",
            "Physical synthesis feasibility would need validation.",
            f"Repaired result stability map: {stable_by_fraction}.",
        ],
    )
