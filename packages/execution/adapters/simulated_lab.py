from packages.models import ExecutionEvent, ExecutionLog


RAW_RESULT_CSV = """candidate_id,mn_pct,e_hull,cond_proxy,stable
LiFePO4_12,12,0.039,1.18,true
LiFePO4_14,14,0.046,1.22,true
LiFePO4_16,16,0.055,1.24,false"""


def execute_simulated_lab() -> ExecutionLog:
    return ExecutionLog(
        execution_id="EXE-001",
        status="completed_with_recovery_needed",
        events=[
            ExecutionEvent(
                timestamp="09:00",
                step_id="S1",
                event_type="started",
                message="Candidate batch preparation started.",
            ),
            ExecutionEvent(
                timestamp="09:50",
                step_id="S3",
                event_type="completed",
                message="Structure validation completed for 12%, 14%, and 16% Mn.",
            ),
            ExecutionEvent(
                timestamp="10:05",
                step_id="S4",
                event_type="started",
                message="Property prediction started.",
            ),
            ExecutionEvent(
                timestamp="10:14",
                step_id="S4",
                event_type="failure",
                message="Property predictor timeout for 14% Mn condition.",
            ),
            ExecutionEvent(
                timestamp="10:22",
                step_id="S4",
                event_type="completed",
                message="Retry completed for 14% Mn condition.",
            ),
        ],
        raw_result_csv=RAW_RESULT_CSV,
    )

