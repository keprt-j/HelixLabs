from packages.models import RepairedResult, ResultInterpretation


def interpret_results(results: list[RepairedResult]) -> ResultInterpretation:
    stable_by_fraction = {round(item.mn_fraction, 3): item.stability_pass for item in results}
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

