from packages.models import LiteratureQueryPlan, ScientificIntent


def build_query_plan(intent: ScientificIntent | None = None) -> LiteratureQueryPlan:
    base_material = intent.base_material if intent else "LiFePO4"
    intervention = intent.intervention if intent else "Mn doping"
    material_synonym = (intent.synonyms.get(base_material, ["lithium iron phosphate"])[0] if intent else "lithium iron phosphate")
    intervention_synonym = (intent.synonyms.get(intervention, ["manganese substitution"])[0] if intent else "manganese substitution")
    return LiteratureQueryPlan(
        exact_queries=[
            f"\"{base_material}\" \"{intervention}\" conductivity stability",
            f"\"{material_synonym}\" {intervention_synonym} cathode",
        ],
        broad_queries=[
            f"{intervention_synonym} {material_synonym} cathode conductivity",
            f"{base_material} dopant screen structural stability",
        ],
        negative_result_queries=[
            f"{base_material} {intervention} instability",
            f"{intervention_synonym} {base_material} failed stability",
        ],
        protocol_queries=[
            f"{base_material} manganese doping synthesis protocol",
            f"{material_synonym} dopant screening method",
        ],
    )
