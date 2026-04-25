from packages.models import ResearchPlan, ScientificIntent


def intent_from_research_plan(plan: ResearchPlan) -> ScientificIntent:
    synonyms = {item.term: item.synonyms for item in plan.synonyms}
    return ScientificIntent(
        domain=plan.domain,
        objective=plan.objective,
        base_material=plan.system,
        intervention=plan.intervention,
        target_property=plan.target_property,
        must_preserve=plan.preserve_property,
        constraints={
            "variable_name": plan.variable_name,
            "variable_label": plan.variable_label,
            "variable_unit": plan.variable_unit,
            "max_runtime_hours": 4,
        },
        success_metrics=plan.success_metrics,
        primary_question=plan.primary_question,
        search_entities=plan.search_entities,
        synonyms=synonyms,
    )
