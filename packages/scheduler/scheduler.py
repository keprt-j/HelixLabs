from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from packages.models import LabResource, Protocol, Schedule, ScheduledTask
from packages.storage import load_json


def schedule_protocol(root: Path, protocol: Protocol) -> Schedule:
    resources = [LabResource.model_validate(item) for item in load_json(root, "data/lab_resources.json")]
    resource_by_type = {resource.type: resource for resource in resources}
    task_end: dict[str, datetime] = {}
    scheduled: list[ScheduledTask] = []

    for step in protocol.steps:
        resource = resource_by_type[step.resource_type]
        resource_available = _parse_time(resource.available_at)
        dependency_end = max([task_end[dep] for dep in step.depends_on], default=resource_available)
        start = max(resource_available, dependency_end)
        end = start + timedelta(minutes=step.duration_minutes)
        task_end[step.step_id] = end
        resource.available_at = _format_time(end)
        scheduled.append(
            ScheduledTask(
                step_id=step.step_id,
                resource_id=resource.resource_id,
                start=_format_time(start),
                end=_format_time(end),
            )
        )
    return Schedule(schedule_id="SCH-001", scheduled_tasks=scheduled, priority_score=0.82)


def _parse_time(value: str) -> datetime:
    return datetime.strptime(value, "%H:%M")


def _format_time(value: datetime) -> str:
    return value.strftime("%H:%M")

