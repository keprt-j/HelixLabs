from packages.models import ScientificIntent


def parse_scientific_intent(user_goal: str) -> ScientificIntent:
    return ScientificIntent(
        domain="materials_discovery",
        objective="optimize_cobalt_free_cathode",
        base_material="LiFePO4",
        intervention="Mn doping",
        target_property="conductivity_proxy",
        must_preserve="thermodynamic_stability",
        constraints={
            "exclude_elements": ["Co", "Ni"],
            "prefer_low_cost": True,
            "max_runtime_hours": 4,
        },
        success_metrics=[
            "energy_above_hull",
            "conductivity_proxy",
            "stability_pass",
        ],
        primary_question="Does moderate Mn doping improve conductivity while preserving stability?",
        search_entities=[
            "LiFePO4",
            "lithium iron phosphate",
            "Mn doping",
            "manganese substitution",
            "cathode",
            "conductivity",
            "stability",
        ],
        synonyms={
            "Mn doping": ["manganese substitution", "Mn-substituted", "manganese-doped"],
            "LiFePO4": ["lithium iron phosphate", "LFP"],
        },
    )

