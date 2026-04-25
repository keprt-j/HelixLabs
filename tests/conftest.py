from __future__ import annotations

import shutil
from pathlib import Path

import pytest

import apps.api.main as api_main
from packages.models import LiteratureQueryPlan, ResearchClaimSeed, ResearchInterpretationSeed, ResearchPlan, RetrievedPaper, SimulatedResultSeed, SynonymSet
from packages.storage import JsonStore
from packages.workflow import HelixWorkflow


@pytest.fixture(autouse=True)
def isolated_backend_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    shutil.copytree(repo_root / "data", tmp_path / "data", ignore=shutil.ignore_patterns("runtime"))

    store = JsonStore(tmp_path)
    workflow = HelixWorkflow(tmp_path, store)
    monkeypatch.setattr(api_main, "store", store)
    monkeypatch.setattr(api_main, "workflow", workflow)
    monkeypatch.setattr("packages.workflow.generate_research_plan", fake_research_plan)
    monkeypatch.setattr("packages.workflow.search_literature", fake_search_literature)


def fake_research_plan(user_goal: str) -> ResearchPlan:
    if "perovskite" in user_goal.lower():
        return _plan(
            domain="materials_discovery",
            objective="Optimize a perovskite solar absorber.",
            system="mixed-halide perovskite absorber",
            intervention="bromide iodide ratio tuning",
            variable_name="bromide_fraction",
            variable_label="bromide fraction",
            variable_unit="",
            target_property="efficiency",
            preserve_property="phase stability",
            prior_values=[0.0, 0.1, 0.2],
            failed_values=[0.5],
            candidate_values=[0.25, 0.3, 0.35],
            next_values=[0.28, 0.32, 0.34],
            controls=["iodide_only_control", "prior_20pct_bromide_baseline"],
            protocol_name="Perovskite Halide Boundary Screen",
        )
    if "enzyme" in user_goal.lower() or "buffer" in user_goal.lower():
        return _plan(
            domain="protein_engineering",
            objective="Optimize enzyme buffer conditions.",
            system="target enzyme buffer system",
            intervention="alkaline pH adjustment",
            variable_name="ph",
            variable_label="pH",
            variable_unit="",
            target_property="activity",
            preserve_property="fold stability",
            prior_values=[7.0, 7.5, 8.0],
            failed_values=[9.5],
            candidate_values=[8.2, 8.5, 8.8],
            next_values=[8.6, 8.7, 8.9],
            controls=["neutral_buffer_control", "prior_pH_8_baseline"],
            protocol_name="Enzyme pH Boundary Screen",
        )
    return _plan(
        domain="materials_discovery",
        objective="Find a low-cost cobalt-free cathode material.",
        system="LiFePO4",
        intervention="Mn doping",
        variable_name="mn_fraction",
        variable_label="Mn",
        variable_unit="%",
        target_property="conductivity_proxy",
        preserve_property="stability",
        prior_values=[0.0, 0.05, 0.1],
        failed_values=[0.2],
        candidate_values=[0.12, 0.14, 0.16],
        next_values=[0.145, 0.15, 0.155],
        controls=["undoped_LiFePO4", "prior_10pct_Mn_baseline"],
        protocol_name="LiFePO4 Mn Boundary Screen",
    )


def _plan(
    *,
    domain: str,
    objective: str,
    system: str,
    intervention: str,
    variable_name: str,
    variable_label: str,
    variable_unit: str,
    target_property: str,
    preserve_property: str,
    prior_values: list[float],
    failed_values: list[float],
    candidate_values: list[float],
    next_values: list[float],
    controls: list[str],
    protocol_name: str,
) -> ResearchPlan:
    failed_label = _label(failed_values[0], variable_label, variable_unit)
    prior_label = ", ".join(_label(value, variable_label, variable_unit) for value in prior_values)
    return ResearchPlan(
        extraction_mode="pytest_mock_llm",
        domain=domain,
        objective=objective,
        system=system,
        intervention=intervention,
        variable_name=variable_name,
        variable_label=variable_label,
        variable_unit=variable_unit,
        target_property=target_property,
        preserve_property=preserve_property,
        success_metrics=["energy_above_hull", target_property, "stability_pass"],
        primary_question=f"Does {intervention} improve {target_property} without hurting {preserve_property}?",
        search_entities=[system, intervention, target_property, preserve_property],
        synonyms=[SynonymSet(term=system, synonyms=[system]), SynonymSet(term=intervention, synonyms=[intervention])],
        hypothesis=f"A boundary screen can locate useful {variable_label} values for {system}.",
        prior_tested_values=prior_values,
        known_failed_values=failed_values,
        candidate_values=candidate_values,
        next_values=next_values,
        controls=controls,
        already_tested_label=f"{prior_label} were already tested",
        failed_condition_label=failed_label,
        gap=f"The boundary between {_label(prior_values[-1], variable_label, variable_unit)} and {failed_label} remains unresolved.",
        recommendation="Screen inside the unresolved boundary rather than repeat known conditions.",
        claims=[
            ResearchClaimSeed(id="C1", claim=f"{system} supports the target experimental system.", status="supported", evidence=["literature"]),
            ResearchClaimSeed(id="C2", claim=f"Prior work does not resolve the {variable_label} boundary.", status="gap", evidence=["prior_work"]),
            ResearchClaimSeed(id="C3", claim=f"Candidate values can improve {target_property} while preserving {preserve_property}.", status="weakest_high_value", evidence=["inference"]),
        ],
        protocol_name=protocol_name,
        candidate_prefix="candidate",
        drifted_variable_column=variable_name.replace("_fraction", "_pct") if variable_name.endswith("_fraction") else variable_name,
        drifted_primary_metric_column="e_hull",
        drifted_target_metric_column="cond_proxy",
        drifted_pass_column="stable",
        simulated_results=[
            SimulatedResultSeed(candidate_id="candidate_1", variable_value=candidate_values[0], primary_metric_value=0.03, target_metric_value=1.25, stability_pass=True),
            SimulatedResultSeed(candidate_id="candidate_2", variable_value=candidate_values[1], primary_metric_value=0.04, target_metric_value=1.36, stability_pass=True),
            SimulatedResultSeed(candidate_id="candidate_3", variable_value=candidate_values[2], primary_metric_value=0.08, target_metric_value=1.45, stability_pass=False),
        ],
        interpretation=ResearchInterpretationSeed(
            observed_results=[
                f"{_label(candidate_values[0], variable_label, variable_unit)} passed the preservation criterion.",
                f"{_label(candidate_values[1], variable_label, variable_unit)} passed the preservation criterion.",
                f"{_label(candidate_values[2], variable_label, variable_unit)} failed the preservation criterion.",
            ],
            inference=f"The useful region likely lies below {_label(candidate_values[2], variable_label, variable_unit)}.",
            uncertainty=f"The exact boundary between {_label(candidate_values[1], variable_label, variable_unit)} and {_label(candidate_values[2], variable_label, variable_unit)} is unresolved.",
            limitations=["Simulated data is for workflow validation, not scientific conclusion."],
        ),
    )


def fake_search_literature(*_args: object, **_kwargs: object) -> tuple[LiteratureQueryPlan, list[RetrievedPaper], str]:
    query_plan = LiteratureQueryPlan(
        exact_queries=['"LiFePO4" "Mn doping" conductivity stability'],
        broad_queries=["manganese substitution lithium iron phosphate cathode conductivity"],
        negative_result_queries=["LiFePO4 Mn doping instability"],
        protocol_queries=["LiFePO4 manganese doping synthesis protocol"],
    )
    papers = [
        RetrievedPaper(
            paper_id="TEST-1",
            title="Low manganese substitution in LiFePO4 cathodes",
            abstract="0%, 5%, and 10% Mn tests improved conductivity while retaining stability.",
            authors=["A. Researcher"],
            year=2024,
            venue="Pytest",
            doi="10.0000/test-low",
            url=None,
            source="test",
            retrieval_mode="live",
        ),
        RetrievedPaper(
            paper_id="TEST-2",
            title="High manganese instability in LiFePO4",
            abstract="20% Mn failed stability while conductivity increased.",
            authors=["B. Researcher"],
            year=2024,
            venue="Pytest",
            doi="10.0000/test-high",
            url=None,
            source="test",
            retrieval_mode="live",
        ),
    ]
    return query_plan, papers, "live"


def _label(value: float, variable_label: str, variable_unit: str) -> str:
    if variable_unit == "%":
        return f"{value * 100:g}% {variable_label}"
    if variable_label.lower() == "ph":
        return f"pH {value:g}"
    return f"{variable_label} {value:g}"
