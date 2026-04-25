from fastapi.testclient import TestClient

from apps.api.main import app
from packages.literature.deduplicator import dedupe_papers
from packages.models import RetrievedPaper
from packages.workflow import CANONICAL_GOAL


client = TestClient(app)


def test_required_evidence_endpoints_find_canonical_gap() -> None:
    run_id = client.post("/api/runs", json={"user_goal": CANONICAL_GOAL}).json()["run"]["id"]

    parsed = client.post(f"/api/runs/{run_id}/parse-goal")
    assert parsed.status_code == 200
    assert parsed.json()["scientific_intent"]["base_material"] == "LiFePO4"

    searched = client.post(f"/api/runs/{run_id}/search-literature")
    assert searched.status_code == 200
    search_payload = searched.json()
    assert search_payload["retrieval_mode"] == "live"
    assert "\"LiFePO4\" \"Mn doping\" conductivity stability" in search_payload["query_plan"]["exact_queries"]
    assert len(search_payload["retrieved_papers"]) >= 2

    matched = client.post(f"/api/runs/{run_id}/match-prior-work")
    assert matched.status_code == 200
    prior = matched.json()["prior_work_match"]
    tested_conditions = {
        condition
        for match in prior["matches"]
        for condition in match["tested_conditions"]
    }
    assert {"0% Mn", "5% Mn", "10% Mn", "20% Mn"}.issubset(tested_conditions)
    assert prior["gap"] == "The boundary between 10% Mn and 20% Mn remains unresolved."

    negative = client.post(f"/api/runs/{run_id}/check-negative-results")
    assert negative.status_code == 200
    negative_results = negative.json()["negative_results"]
    assert negative_results[0]["failed_condition"] == "20% Mn"
    assert negative_results[0]["failure_type"] == "stability_threshold_failed"

    payload = client.get(f"/api/runs/{run_id}").json()
    event_types = [event["event_type"] for event in payload["provenance_events"]]
    assert event_types == [
        "run_created",
        "goal_parsed",
        "literature_searched",
        "prior_work_matched",
        "negative_results_checked",
    ]


def test_deduplicator_prefers_doi_and_normalized_titles() -> None:
    papers = [
        _paper("P1", "Manganese-substituted lithium iron phosphate cathodes", "10.0000/example"),
        _paper("P2", "Different title for same DOI", "10.0000/example"),
        _paper("P3", "Boundary effects in manganese doped LiFePO4", None),
        _paper("P4", "Boundary effects in manganese-doped LiFePO4", None),
    ]

    unique = dedupe_papers(papers)

    assert [paper.paper_id for paper in unique] == ["P1", "P3"]


def test_literature_endpoint_uses_live_search_boundary_mock() -> None:
    run_id = client.post("/api/runs", json={"user_goal": CANONICAL_GOAL}).json()["run"]["id"]
    client.post(f"/api/runs/{run_id}/parse-goal")

    response = client.post(f"/api/runs/{run_id}/search-literature")

    assert response.status_code == 200
    assert response.json()["retrieval_mode"] == "live"
    assert all(paper["retrieval_mode"] == "live" for paper in response.json()["retrieved_papers"])


def _paper(paper_id: str, title: str, doi: str | None) -> RetrievedPaper:
    return RetrievedPaper(
        paper_id=paper_id,
        title=title,
        abstract="LiFePO4 manganese cathode conductivity stability",
        authors=["A. Researcher"],
        year=2024,
        venue="Test",
        doi=doi,
        url=None,
        source="test",
        retrieval_mode="live",
    )
