from fastapi.testclient import TestClient

from apps.api.main import app


client = TestClient(app)


def test_perovskite_prompt_runs_with_llm_research_plan() -> None:
    payload = _run_to_memory_updated(
        "Optimize a perovskite solar absorber and test whether bromide iodide ratio tuning improves efficiency without hurting phase stability."
    )
    artifacts = payload["artifacts"]

    assert artifacts["research_plan"]["extraction_mode"] == "pytest_mock_llm"
    assert artifacts["scientific_intent"]["constraints"]["variable_name"] == "bromide_fraction"
    assert artifacts["experiment_ir"]["variables"]["bromide_fraction"] == [0.25, 0.3, 0.35]
    assert artifacts["negative_results"][0]["failed_condition"] == "bromide fraction 0.5"
    assert artifacts["repaired_results"][0]["bromide_fraction"] == 0.25
    assert artifacts["next_experiment_recommendation"]["candidate_next_experiments"][0]["conditions"] == [0.28, 0.32, 0.34]


def test_enzyme_prompt_runs_with_llm_research_plan() -> None:
    payload = _run_to_memory_updated(
        "Find the best enzyme buffer pH and test whether mildly alkaline conditions improve activity without hurting fold stability."
    )
    artifacts = payload["artifacts"]

    assert artifacts["scientific_intent"]["domain"] == "protein_engineering"
    assert artifacts["experiment_ir"]["variables"]["ph"] == [8.2, 8.5, 8.8]
    assert artifacts["negative_results"][0]["failed_condition"] == "pH 9.5"
    assert artifacts["repaired_results"][2]["stability_pass"] is False
    assert "pH" in artifacts["next_experiment_recommendation"]["selected_next_experiment"]


def _run_to_memory_updated(goal: str) -> dict:
    created = client.post("/api/runs", json={"user_goal": goal})
    assert created.status_code == 200
    run_id = created.json()["run"]["id"]
    for _ in range(30):
        payload = client.get(f"/api/runs/{run_id}").json()
        state = payload["run"]["state"]
        if state == "MEMORY_UPDATED":
            return payload
        if state == "AWAITING_HUMAN_APPROVAL":
            response = client.post(
                f"/api/runs/{run_id}/approve",
                json={"approved": True, "approved_by": "pytest", "notes": "ok"},
            )
        else:
            response = client.post(f"/api/runs/{run_id}/advance")
        assert response.status_code == 200
    raise AssertionError("run did not reach MEMORY_UPDATED")
