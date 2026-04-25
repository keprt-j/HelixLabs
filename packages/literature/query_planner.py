from packages.models import LiteratureQueryPlan


def build_query_plan() -> LiteratureQueryPlan:
    return LiteratureQueryPlan(
        exact_queries=[
            "\"LiFePO4\" \"Mn doping\" conductivity stability",
            "\"lithium iron phosphate\" manganese substitution cathode",
        ],
        broad_queries=[
            "manganese doped lithium iron phosphate cathode conductivity",
            "LiFePO4 dopant screen structural stability",
        ],
        negative_result_queries=[
            "LiFePO4 Mn doping instability",
            "manganese substituted LiFePO4 failed stability",
        ],
        protocol_queries=[
            "LiFePO4 manganese doping synthesis protocol",
            "lithium iron phosphate dopant screening method",
        ],
    )

