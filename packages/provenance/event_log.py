from __future__ import annotations

from typing import Any

from packages.models import ProvenanceEvent
from packages.storage import JsonStore


def record_event(
    store: JsonStore,
    run_id: str,
    event_type: str,
    summary: str,
    actor: str,
    payload: dict[str, Any] | None = None,
) -> ProvenanceEvent:
    event_number = len(store.get_events(run_id)) + 1
    event = ProvenanceEvent(
        event_id=f"PE-{event_number:03d}",
        run_id=run_id,
        event_type=event_type,
        summary=summary,
        actor=actor,
        payload=payload or {},
    )
    return store.add_event(event)
