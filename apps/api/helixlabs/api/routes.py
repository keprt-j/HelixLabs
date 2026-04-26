from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from helixlabs.api.schemas import (
    AdvanceResponse,
    ApproveRequest,
    EventsResponse,
    RunCreateRequest,
    RunDetailResponse,
    RunListItem,
    RunListResponse,
    RunSummaryResponse,
    SimulationOverridesRequest,
    StageResponse,
)
from helixlabs.core.dependencies import orchestrator
from helixlabs.domain.models import RunState

router = APIRouter(prefix="/api", tags=["runs"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/runs", response_model=RunSummaryResponse)
def create_run(payload: RunCreateRequest) -> RunSummaryResponse:
    run_id = f"RUN-{datetime.now(tz=timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
    run = orchestrator.create_run(
        run_id=run_id,
        user_goal=payload.user_goal,
        plugin_override=payload.plugin_override,
        simulation_overrides=payload.simulation_overrides,
    )
    return RunSummaryResponse(run_id=run.run_id, state=run.state, summary="Run created and intake completed")


@router.get("/runs", response_model=RunListResponse)
def list_runs(limit: int = 50) -> RunListResponse:
    runs = orchestrator.list_runs(limit=max(1, min(200, limit)))
    items = [
        RunListItem(run_id=r.run_id, state=r.state, user_goal=r.user_goal, updated_at=r.updated_at)
        for r in runs
    ]
    return RunListResponse(runs=items)


@router.get("/runs/{run_id}", response_model=RunDetailResponse)
def get_run(run_id: str) -> RunDetailResponse:
    run = orchestrator.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return RunDetailResponse(run=run)


@router.post("/runs/{run_id}/advance", response_model=AdvanceResponse)
def advance_run(run_id: str) -> AdvanceResponse:
    run = orchestrator.advance(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return AdvanceResponse(run=run)


@router.post("/runs/{run_id}/approve", response_model=StageResponse)
def approve_run(run_id: str, payload: ApproveRequest) -> StageResponse:
    run = orchestrator.approve(
        run_id=run_id,
        approved=payload.approved,
        approved_by=payload.approved_by,
        notes=payload.notes,
    )
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    if not payload.approved:
        raise HTTPException(status_code=400, detail="Approval rejected")
    if run.state != RunState.APPROVED:
        raise HTTPException(status_code=409, detail="Run is not awaiting human approval")
    return StageResponse(run=run, stage="approve", message="Approval event recorded")


@router.post("/runs/{run_id}/simulation-overrides", response_model=RunDetailResponse)
def set_simulation_overrides(run_id: str, payload: SimulationOverridesRequest) -> RunDetailResponse:
    run = orchestrator.set_simulation_overrides(run_id, payload.simulation_overrides)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return RunDetailResponse(run=run)


@router.post("/runs/{run_id}/replan", response_model=RunDetailResponse)
def replan(run_id: str) -> RunDetailResponse:
    try:
        run = orchestrator.replan(run_id)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return RunDetailResponse(run=run)


@router.get("/runs/{run_id}/report", response_model=RunDetailResponse)
def get_report(run_id: str) -> RunDetailResponse:
    run = orchestrator.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    if run.state not in {RunState.REPORT_GENERATED, RunState.MEMORY_UPDATED}:
        raise HTTPException(status_code=409, detail="Run has not reached outcomes stage")
    return RunDetailResponse(run=run)


@router.get("/runs/{run_id}/events", response_model=EventsResponse)
def get_run_events(run_id: str) -> EventsResponse:
    run = orchestrator.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return EventsResponse(run_id=run.run_id, events=run.provenance)


def _stage_handler(run_id: str, stage_name: str) -> StageResponse:
    try:
        run = orchestrator.run_stage(run_id=run_id, stage_name=stage_name)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return StageResponse(run=run, stage=stage_name, message=f"Stage '{stage_name}' executed")


@router.post("/runs/{run_id}/parse-goal", response_model=StageResponse)
def parse_goal(run_id: str) -> StageResponse:
    return _stage_handler(run_id, "parse-goal")


@router.post("/runs/{run_id}/search-literature", response_model=StageResponse)
def search_literature(run_id: str) -> StageResponse:
    return _stage_handler(run_id, "search-literature")


@router.post("/runs/{run_id}/match-prior-work", response_model=StageResponse)
def match_prior_work(run_id: str) -> StageResponse:
    return _stage_handler(run_id, "match-prior-work")


@router.post("/runs/{run_id}/check-negative-results", response_model=StageResponse)
def check_negative_results(run_id: str) -> StageResponse:
    return _stage_handler(run_id, "check-negative-results")


@router.post("/runs/{run_id}/build-claim-graph", response_model=StageResponse)
def build_claim_graph(run_id: str) -> StageResponse:
    return _stage_handler(run_id, "build-claim-graph")


@router.post("/runs/{run_id}/compile-ir", response_model=StageResponse)
def compile_ir(run_id: str) -> StageResponse:
    return _stage_handler(run_id, "compile-ir")


@router.post("/runs/{run_id}/validate-feasibility", response_model=StageResponse)
def validate_feasibility(run_id: str) -> StageResponse:
    return _stage_handler(run_id, "validate-feasibility")


@router.post("/runs/{run_id}/score-value", response_model=StageResponse)
def score_value(run_id: str) -> StageResponse:
    return _stage_handler(run_id, "score-value")


@router.post("/runs/{run_id}/generate-protocol", response_model=StageResponse)
def generate_protocol(run_id: str) -> StageResponse:
    return _stage_handler(run_id, "generate-protocol")


@router.post("/runs/{run_id}/schedule", response_model=StageResponse)
def schedule(run_id: str) -> StageResponse:
    return _stage_handler(run_id, "schedule")


@router.post("/runs/{run_id}/execute", response_model=StageResponse)
def execute(run_id: str) -> StageResponse:
    return _stage_handler(run_id, "execute")


@router.post("/runs/{run_id}/recover", response_model=StageResponse)
def recover(run_id: str) -> StageResponse:
    return _stage_handler(run_id, "recover")


@router.post("/runs/{run_id}/validate-results", response_model=StageResponse)
def validate_results(run_id: str) -> StageResponse:
    return _stage_handler(run_id, "validate-results")


@router.post("/runs/{run_id}/interpret", response_model=StageResponse)
def interpret(run_id: str) -> StageResponse:
    return _stage_handler(run_id, "interpret")


@router.post("/runs/{run_id}/recommend-next", response_model=StageResponse)
def recommend_next(run_id: str) -> StageResponse:
    return _stage_handler(run_id, "recommend-next")


@router.post("/runs/{run_id}/update-memory", response_model=StageResponse)
def update_memory(run_id: str) -> StageResponse:
    return _stage_handler(run_id, "update-memory")
