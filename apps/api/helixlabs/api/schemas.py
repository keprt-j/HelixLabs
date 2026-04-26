from __future__ import annotations

from pydantic import BaseModel, Field

from helixlabs.domain.models import ProvenanceEvent, RunRecord, RunState


class RunCreateRequest(BaseModel):
    user_goal: str = Field(min_length=8, description="Natural-language experiment objective")
    plugin_override: str | None = Field(
        default=None,
        description="Optional execution plugin id override (e.g. chemistry_materials, generic_blackbox)",
    )
    simulation_overrides: dict[str, str | int | float] | None = Field(
        default=None,
        description="Optional per-run simulation controls (noise, replicates, design density, seed).",
    )


class SimulationOverridesRequest(BaseModel):
    simulation_overrides: dict[str, str | int | float] = Field(
        description="Per-run simulation controls (noise, replicates, design density, seed).",
    )


class RunSummaryResponse(BaseModel):
    run_id: str
    state: RunState
    summary: str


class RunListItem(BaseModel):
    run_id: str
    state: RunState
    user_goal: str
    updated_at: str


class RunListResponse(BaseModel):
    runs: list[RunListItem]


class RunDetailResponse(BaseModel):
    run: RunRecord


class AdvanceResponse(BaseModel):
    run: RunRecord


class EventsResponse(BaseModel):
    run_id: str
    events: list[ProvenanceEvent]


class ApproveRequest(BaseModel):
    approved: bool = True
    approved_by: str = "demo_user"
    notes: str = ""


class StageResponse(BaseModel):
    run: RunRecord
    stage: str
    message: str

