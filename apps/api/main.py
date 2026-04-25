from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from packages.models import STATE_SEQUENCE  # noqa: E402
from packages.storage import JsonStore  # noqa: E402
from packages.workflow import CANONICAL_GOAL, HelixWorkflow, WorkflowError  # noqa: E402

store = JsonStore(ROOT)
workflow = HelixWorkflow(ROOT, store)

app = FastAPI(title="HelixLabs API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CreateRunRequest(BaseModel):
    user_goal: str = CANONICAL_GOAL


class ApprovalRequest(BaseModel):
    approved: bool = True
    approved_by: str = "demo_user"
    notes: str = "Approved narrowed screen after prior-work check."


@app.exception_handler(WorkflowError)
async def workflow_exception_handler(_request: Request, exc: WorkflowError) -> JSONResponse:
    status_code = 409 if exc.code in {"INVALID_STATE_TRANSITION", "APPROVAL_REQUIRED"} else 400
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": exc.code, "message": str(exc), "details": exc.details}},
    )


@app.exception_handler(KeyError)
async def key_error_handler(_request: Request, exc: KeyError) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"error": {"code": "RUN_NOT_FOUND", "message": f"Run {exc.args[0]} was not found.", "details": {}}},
    )


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "states": [state.value for state in STATE_SEQUENCE]}


@app.post("/api/runs")
def create_run(request: CreateRunRequest) -> dict[str, Any]:
    run = workflow.create_run(request.user_goal)
    return {"run": run.model_dump(mode="json")}


@app.get("/api/runs/{run_id}")
def get_run(run_id: str) -> dict[str, Any]:
    return workflow.get_payload(run_id)


@app.post("/api/runs/{run_id}/advance")
def advance_run(run_id: str) -> dict[str, Any]:
    return workflow.advance(run_id)


@app.post("/api/runs/{run_id}/parse-goal")
def parse_goal(run_id: str) -> dict[str, Any]:
    return workflow.parse_goal(run_id)


@app.post("/api/runs/{run_id}/search-literature")
def search_literature(run_id: str) -> dict[str, Any]:
    return workflow.search_literature(run_id)


@app.post("/api/runs/{run_id}/match-prior-work")
def match_prior_work(run_id: str) -> dict[str, Any]:
    return workflow.match_prior_work(run_id)


@app.post("/api/runs/{run_id}/check-negative-results")
def check_negative_results(run_id: str) -> dict[str, Any]:
    return workflow.check_negative_results(run_id)


@app.post("/api/runs/{run_id}/build-claim-graph")
def build_claim_graph(run_id: str) -> dict[str, Any]:
    return workflow.build_claim_graph(run_id)


@app.post("/api/runs/{run_id}/compile-ir")
def compile_ir(run_id: str) -> dict[str, Any]:
    return workflow.compile_ir(run_id)


@app.post("/api/runs/{run_id}/validate-feasibility")
def validate_feasibility(run_id: str) -> dict[str, Any]:
    return workflow.validate_feasibility(run_id)


@app.post("/api/runs/{run_id}/score-value")
def score_value(run_id: str) -> dict[str, Any]:
    return workflow.score_value(run_id)


@app.post("/api/runs/{run_id}/generate-protocol")
def generate_protocol(run_id: str) -> dict[str, Any]:
    return workflow.generate_protocol(run_id)


@app.post("/api/runs/{run_id}/schedule")
def schedule(run_id: str) -> dict[str, Any]:
    return workflow.schedule(run_id)


@app.post("/api/runs/{run_id}/approve")
def approve(run_id: str, request: ApprovalRequest) -> dict[str, Any]:
    return workflow.approve(run_id, request.approved, request.approved_by, request.notes)


@app.post("/api/runs/{run_id}/execute")
def execute(run_id: str) -> dict[str, Any]:
    return workflow.execute(run_id)


@app.post("/api/runs/{run_id}/recover")
def recover(run_id: str) -> dict[str, Any]:
    return workflow.recover(run_id)


@app.post("/api/runs/{run_id}/validate-results")
def validate_results(run_id: str) -> dict[str, Any]:
    return workflow.validate_results(run_id)


@app.post("/api/runs/{run_id}/interpret")
def interpret(run_id: str) -> dict[str, Any]:
    return workflow.interpret(run_id)


@app.post("/api/runs/{run_id}/recommend-next")
def recommend_next(run_id: str) -> dict[str, Any]:
    return workflow.recommend_next(run_id)


@app.post("/api/runs/{run_id}/update-memory")
def update_memory(run_id: str) -> dict[str, Any]:
    return workflow.update_memory(run_id)


@app.get("/api/runs/{run_id}/report")
def get_report(run_id: str) -> dict[str, Any]:
    return workflow.get_report(run_id)
