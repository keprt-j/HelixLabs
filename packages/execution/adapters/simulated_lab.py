from packages.models import ExecutionEvent, ExecutionLog, ResearchPlan


RAW_RESULT_CSV = """candidate_id,mn_pct,e_hull,cond_proxy,stable
LiFePO4_12,12,0.039,1.18,true
LiFePO4_14,14,0.046,1.22,true
LiFePO4_16,16,0.055,1.24,false"""


def execute_simulated_lab(plan: ResearchPlan | None = None) -> ExecutionLog:
    raw_result_csv = _plan_csv(plan) if plan else RAW_RESULT_CSV
    variable_label = plan.variable_label if plan else "Mn"
    values = ", ".join(str(value) for value in (plan.candidate_values if plan else ["12%", "14%", "16%"]))
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
                message=f"Validation completed for {values} {variable_label}.",
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
                message=f"Property predictor timeout for middle {variable_label} condition.",
            ),
            ExecutionEvent(
                timestamp="10:22",
                step_id="S4",
                event_type="completed",
                message=f"Retry completed for middle {variable_label} condition.",
            ),
        ],
        raw_result_csv=raw_result_csv,
    )


def _plan_csv(plan: ResearchPlan | None) -> str:
    if plan is None:
        return RAW_RESULT_CSV
    header = [
        "candidate_id",
        plan.drifted_variable_column,
        plan.drifted_primary_metric_column,
        plan.drifted_target_metric_column,
        plan.drifted_pass_column,
    ]
    lines = [",".join(header)]
    for row in plan.simulated_results:
        lines.append(
            ",".join(
                [
                    row.candidate_id,
                    str(row.variable_value),
                    str(row.primary_metric_value),
                    str(row.target_metric_value),
                    str(row.stability_pass).lower(),
                ]
            )
        )
    return "\n".join(lines)
