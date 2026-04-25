from fastapi.testclient import TestClient

from apps.api.main import app
from packages.workflow import CANONICAL_GOAL


client = TestClient(app)


def test_canonical_demo_path_end_to_end() -> None:
    created = client.post("/api/runs", json={"user_goal": CANONICAL_GOAL})
    assert created.status_code == 200
    run_id = created.json()["run"]["id"]

    expected_states = [
        "GOAL_PARSED",
        "LITERATURE_SEARCHED",
        "PRIOR_WORK_MATCHED",
        "NEGATIVE_RESULTS_CHECKED",
        "CLAIM_GRAPH_BUILT",
        "EXPERIMENT_IR_COMPILED",
        "FEASIBILITY_VALIDATED",
        "NOVELTY_VALUE_SCORED",
        "PROTOCOL_GENERATED",
        "SCHEDULED",
        "AWAITING_HUMAN_APPROVAL",
    ]
    for state in expected_states:
        response = client.post(f"/api/runs/{run_id}/advance")
        assert response.status_code == 200
        assert response.json()["new_state"] == state

    blocked = client.post(f"/api/runs/{run_id}/advance")
    assert blocked.status_code == 409
    assert blocked.json()["error"]["code"] == "APPROVAL_REQUIRED"

    approved = client.post(f"/api/runs/{run_id}/approve", json={"approved": True, "approved_by": "pytest", "notes": "ok"})
    assert approved.status_code == 200
    assert approved.json()["state"] == "APPROVED"

    for state in [
        "EXECUTION_FAILED_OR_COMPLETED",
        "RECOVERY_APPLIED",
        "RESULTS_COLLECTED",
        "RESULTS_REPAIRED",
        "INTERPRETED",
        "NEXT_EXPERIMENT_RECOMMENDED",
        "REPORT_GENERATED",
        "MEMORY_UPDATED",
    ]:
        response = client.post(f"/api/runs/{run_id}/advance")
        assert response.status_code == 200
        assert response.json()["new_state"] == state

    payload = client.get(f"/api/runs/{run_id}").json()
    artifacts = payload["artifacts"]
    assert artifacts["experiment_ir"]["variables"]["mn_fraction"] == [0.12, 0.14, 0.16]
    assert artifacts["failure_recovery_plan"]["selected_recovery"] == "retry_failed_condition"
    assert artifacts["repaired_results"][1]["mn_fraction"] == 0.14
    assert artifacts["next_experiment_recommendation"]["candidate_next_experiments"][0]["conditions"] == [0.145, 0.15, 0.155]
    assert len(payload["provenance_events"]) >= 20

