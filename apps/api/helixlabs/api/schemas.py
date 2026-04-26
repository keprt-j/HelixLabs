from __future__ import annotations

from pydantic import BaseModel, Field

from helixlabs.domain.models import ProvenanceEvent, RunRecord, RunState


class RunCreateRequest(BaseModel):
    user_goal: str = Field(min_length=8, description="Natural-language experiment objective")


class RunSummaryResponse(BaseModel):
    run_id: str
    state: RunState
    summary: str


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

