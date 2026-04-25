from fastapi.testclient import TestClient

from apps.api.main import app
from packages.models import (
    ExperimentRun,
    ProvenanceEvent,
    RunState,
    ScientificIntent,
)
from packages.workflow import CANONICAL_GOAL


client = TestClient(app)


def test_create_and_get_run_records_provenance_event() -> None:
    created = client.post("/api/runs", json={"user_goal": CANONICAL_GOAL})

    assert created.status_code == 200
    run = ExperimentRun.model_validate(created.json()["run"])
    assert run.id.startswith("RUN-")
    assert run.state == RunState.CREATED

    fetched = client.get(f"/api/runs/{run.id}")
    assert fetched.status_code == 200
    payload = fetched.json()
    assert payload["run"]["state"] == "CREATED"
    assert len(payload["provenance_events"]) == 1

    event = ProvenanceEvent.model_validate(payload["provenance_events"][0])
    assert event.event_type == "run_created"
    assert event.run_id == run.id


def test_advance_from_created_parses_goal_and_records_provenance() -> None:
    run_id = client.post("/api/runs", json={"user_goal": CANONICAL_GOAL}).json()["run"]["id"]

    advanced = client.post(f"/api/runs/{run_id}/advance")

    assert advanced.status_code == 200
    assert advanced.json()["previous_state"] == "CREATED"
    assert advanced.json()["new_state"] == "GOAL_PARSED"
    assert advanced.json()["artifact_created"] == "scientific_intent"

    payload = client.get(f"/api/runs/{run_id}").json()
    intent = ScientificIntent.model_validate(payload["artifacts"]["scientific_intent"])
    assert intent.base_material == "LiFePO4"
    assert intent.intervention == "Mn doping"
    assert [event["event_type"] for event in payload["provenance_events"]] == [
        "run_created",
        "goal_parsed",
    ]


def test_invalid_direct_stage_transition_uses_contract_error_shape() -> None:
    run_id = client.post("/api/runs", json={"user_goal": CANONICAL_GOAL}).json()["run"]["id"]

    response = client.post(f"/api/runs/{run_id}/search-literature")

    assert response.status_code == 409
    assert response.json() == {
        "error": {
            "code": "INVALID_STATE_TRANSITION",
            "message": "Run must be in GOAL_PARSED before this operation.",
            "details": {
                "current_state": "CREATED",
                "required_state": "GOAL_PARSED",
            },
        }
    }


def test_health_exposes_complete_state_sequence() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    states = response.json()["states"]
    assert states[0] == "CREATED"
    assert states[-1] == "MEMORY_UPDATED"
    assert "AWAITING_HUMAN_APPROVAL" in states
